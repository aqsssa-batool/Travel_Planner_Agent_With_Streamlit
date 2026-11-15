"""Core multi-agent trip planner with live weather and currency tools."""
import json
import math
import os
import urllib.parse
import urllib.request
from typing import Any, Callable, Dict, List, Optional, Tuple

from groq import Groq

DEFAULT_MODEL = "openai/gpt-oss-120b"


def _http_json(url: str, timeout: int = 15) -> Dict[str, Any]:
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "WanderWiseTripPlanner/2.0", "Accept": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    data = json.loads(payload)
    if not isinstance(data, dict):
        raise ValueError("The service returned an unexpected response.")
    return data


def _weather_description(code: int) -> str:
    groups = {
        (0,): "Clear sky",
        (1, 2, 3): "Mainly clear / partly cloudy",
        (45, 48): "Fog",
        (51, 53, 55, 56, 57): "Drizzle",
        (61, 63, 65, 66, 67): "Rain",
        (71, 73, 75, 77): "Snow",
        (80, 81, 82): "Rain showers",
        (85, 86): "Snow showers",
        (95, 96, 99): "Thunderstorm",
    }
    for codes, label in groups.items():
        if code in codes:
            return label
    return "Unknown conditions"


def get_weather(city: str) -> Dict[str, Any]:
    """Return current and today's forecast from Open-Meteo; errors are explicit."""
    city = (city or "").strip()
    if not city:
        return {"error": "Enter a city name to check its weather."}

    try:
        geo_url = (
            "https://geocoding-api.open-meteo.com/v1/search?"
            + urllib.parse.urlencode({"name": city, "count": 1, "language": "en", "format": "json"})
        )
        geo = _http_json(geo_url)
        results = geo.get("results") or []
        if not results:
            return {"error": f"I couldn't find a location matching '{city}'. Check the spelling and try again."}

        place = results[0]
        weather_url = "https://api.open-meteo.com/v1/forecast?" + urllib.parse.urlencode({
            "latitude": place["latitude"],
            "longitude": place["longitude"],
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
            "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
            "forecast_days": 1,
            "timezone": "auto",
        })
        data = _http_json(weather_url)
        current = data.get("current") or {}
        daily = data.get("daily") or {}
        if "temperature_2m" not in current:
            raise ValueError("The weather service did not return current conditions.")

        return {
            "source": "live_api",
            "city": ", ".join(filter(None, [place.get("name"), place.get("admin1"), place.get("country")])),
            "local_time": current.get("time"),
            "current_temp_c": current.get("temperature_2m"),
            "feels_like_c": current.get("apparent_temperature"),
            "humidity_percent": current.get("relative_humidity_2m"),
            "wind_speed_kmh": current.get("wind_speed_10m"),
            "precipitation_mm": current.get("precipitation"),
            "condition": _weather_description(int(current.get("weather_code", -1))),
            "forecast_high_c": (daily.get("temperature_2m_max") or [None])[0],
            "forecast_low_c": (daily.get("temperature_2m_min") or [None])[0],
            "rain_chance_percent": (daily.get("precipitation_probability_max") or [None])[0],
            "timezone": data.get("timezone"),
        }
    except Exception as exc:
        return {"error": f"Weather is temporarily unavailable for {city}. Please try again. Details: {exc}"}


SUPPORTED_CURRENCIES = ["USD", "PKR", "EUR", "GBP", "AED", "SAR", "JPY", "CAD", "AUD", "INR", "CHF", "CNY"]


def convert_currency(amount: float, to_currency: str, from_currency: str = "USD") -> Dict[str, Any]:
    """Convert with Open Exchange Rates public endpoint; never invent a fallback quote."""
    source = (from_currency or "USD").strip().upper()
    target = (to_currency or "").strip().upper()
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return {"error": "Enter a valid amount."}
    if not math.isfinite(value) or value < 0:
        return {"error": "Amount must be a finite number greater than or equal to zero."}
    if source not in SUPPORTED_CURRENCIES or target not in SUPPORTED_CURRENCIES:
        return {"error": f"Unsupported currency. Supported currencies: {', '.join(SUPPORTED_CURRENCIES)}."}
    if source == target:
        return {
            "source": "same_currency", "original_amount": value,
            "from_currency": source, "to_currency": target,
            "converted_amount": round(value, 2), "rate": 1.0,
            "exchange_rate": f"1 {source} = 1 {target}", "timestamp": "No conversion needed",
        }

    try:
        data = _http_json("https://open.er-api.com/v6/latest/" + urllib.parse.quote(source))
        if data.get("result") != "success":
            raise ValueError(data.get("error-type", "Exchange-rate service returned an error."))
        rate = (data.get("rates") or {}).get(target)
        if rate is None:
            raise ValueError(f"The live provider does not currently support {target}.")
        rate = float(rate)
        converted = value * rate
        return {
            "source": "live_api", "original_amount": value,
            "from_currency": source, "to_currency": target,
            "converted_amount": round(converted, 2), "rate": rate,
            "exchange_rate": f"1 {source} = {rate:,.6f} {target}",
            "timestamp": data.get("time_last_update_utc", "Provider did not give an update time"),
        }
    except Exception as exc:
        return {"error": f"Live currency conversion is unavailable right now. Please try again later. Details: {exc}"}


TOOLS_SPEC = [
    {"type": "function", "function": {
        "name": "get_weather", "description": "Get current live weather for a destination city.",
        "parameters": {"type": "object", "properties": {"city": {"type": "string"}}, "required": ["city"]},
    }},
    {"type": "function", "function": {
        "name": "convert_currency", "description": "Convert money using the latest available exchange rate.",
        "parameters": {"type": "object", "properties": {
            "amount": {"type": "number"}, "to_currency": {"type": "string"}, "from_currency": {"type": "string"},
        }, "required": ["amount", "to_currency"]},
    }},
]
TOOL_FUNCTIONS = {"get_weather": get_weather, "convert_currency": convert_currency}


class Agent:
    def __init__(self, name: str, role: str, system_prompt: str, client: Groq,
                 model: str = DEFAULT_MODEL, tools=None, tool_functions=None):
        self.name, self.role, self.system_prompt = name, role, system_prompt
        self.client, self.model = client, model
        self.tools = tools
        self.tool_functions = tool_functions or {}

    def run(self, user_message: str, conversation_history=None, status_callback=None) -> Tuple[str, List[Dict[str, Any]]]:
        messages = [{"role": "system", "content": self.system_prompt}]
        if conversation_history:
            messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        logs = []

        for _ in range(6):
            params = {"model": self.model, "messages": messages, "temperature": 0.3}
            if self.tools:
                params.update({"tools": self.tools, "tool_choice": "auto"})
            response = self.client.chat.completions.create(**params)
            msg = response.choices[0].message
            calls = msg.tool_calls
            if not calls:
                return msg.content or "", logs
            messages.append(msg.model_dump(exclude_none=True))
            for call in calls:
                name = call.function.name
                try:
                    args = json.loads(call.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                if status_callback:
                    status_callback(self.name, f"Using {name}")
                try:
                    result = self.tool_functions[name](**args) if name in self.tool_functions else {"error": f"Unknown tool: {name}"}
                except Exception as exc:
                    result = {"error": str(exc)}
                logs.append({"agent": self.name, "tool": name, "arguments": args, "result": result})
                messages.append({"role": "tool", "tool_call_id": call.id, "content": json.dumps(result, ensure_ascii=False)})

        messages.append({"role": "user", "content": "Give your final answer from the tool results. Do not call more tools."})
        response = self.client.chat.completions.create(model=self.model, messages=messages, temperature=0.3)
        return response.choices[0].message.content or "", logs


def create_planner_agent(client, model):
    prompt = """You are the Lead Trip Planner. Return VALID JSON ONLY using this schema:
{"destination":"City", "duration_days":3, "num_people":2, "total_budget":60000, "currency":"PKR", "daily_focus":[{"day":1,"theme":"...","highlights":["..."],"budget_target":1000}], "budget_allocation_targets":{"accommodation":0,"food_and_dining":0,"transportation":0,"attractions_entry":0,"emergency_buffer":0}, "feasibility_notes":"..."}
Use the exact destination, days, travelers, currency and budget from the request. If budget is unspecified, estimate a realistic one and state assumptions. Make daily_focus exactly the requested number of days. Never claim prices are verified unless sourced."""
    return Agent("Planner", "Trip blueprint creator", prompt, client, model)


def create_budget_agent(client, model):
    prompt = """You are the Travel Budget Agent. Analyze the blueprint and original request. Use get_weather for destination weather. Use convert_currency if a currency conversion is needed. Estimate accommodation, food, transport, attractions and emergency buffer. State currency clearly, distinguish estimates from live verified rates/prices, and say whether the plan fits the budget. If a tool reports an error, state that rather than inventing its result."""
    return Agent("Budget Agent", "Financial analyst", prompt, client, model, TOOLS_SPEC, TOOL_FUNCTIONS)


def create_writer_agent(client, model):
    prompt = """You are the Travel Writer. Create a polished, practical Markdown itinerary. Include summary, day-by-day morning/afternoon/evening schedule, dining ideas, itemized budget, live weather only if supplied by tools, packing advice and local travel tips. Clearly label estimates. Do not invent weather, exchange rates, confirmed bookings or guaranteed prices."""
    return Agent("Writer", "Itinerary author", prompt, client, model)


def create_reviewer_agent(client, model):
    prompt = """You are a strict itinerary reviewer. Check exact number of days and travelers, budget, practical timing and internal consistency. If satisfactory start with APPROVED. Otherwise start with REVISE: and list specific corrections. Do not approve a plan that exceeds a stated budget."""
    return Agent("Reviewer", "Quality auditor", prompt, client, model)


def _extract_json(text: str) -> Dict[str, Any]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.rstrip().endswith("```"):
            cleaned = cleaned.rstrip()[:-3].strip()
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start < 0 or end <= start:
            raise ValueError(f"Planner did not return valid JSON: {text[:700]}")
        parsed = json.loads(cleaned[start:end + 1])
    if not isinstance(parsed, dict):
        raise ValueError("Planner response must be a JSON object.")
    return parsed


def orchestrate_trip_planning(trip_request: str, groq_api_key: str,
                               model: str = DEFAULT_MODEL,
                               status_callback: Optional[Callable] = None) -> Dict[str, Any]:
    if not groq_api_key:
        raise ValueError("Groq API key is missing.")
    client = Groq(api_key=groq_api_key)
    planner, budget_agent = create_planner_agent(client, model), create_budget_agent(client, model)
    writer, reviewer = create_writer_agent(client, model), create_reviewer_agent(client, model)

    def log(agent, message, data=None):
        if status_callback:
            status_callback(agent, message, data or {})

    history, feedback = [], ""
    approved, final_itinerary, final_plan, final_budget = False, "", {}, ""
    # The Planner -> Budget -> Writer -> Reviewer cycle repeats until the
    # Reviewer explicitly returns APPROVED. There is no review-round limit.
    iteration = 0
    while not approved:
        iteration += 1
        log("Planner", f"Preparing JSON trip blueprint (review round {iteration})")
        planner_input = (
            "Return a valid JSON object only, following your required trip-plan schema.\n"
            f"Original user request:\n{trip_request}"
            + (f"\n\nREVIEWER FEEDBACK FROM THE PREVIOUS ROUND — you MUST address these corrections in the revised JSON plan:\n{feedback}" if feedback else "")
        )
        planner_text, _ = planner.run(planner_input)
        final_plan = _extract_json(planner_text)
        # Ensure the JSON blueprint retains the user's core trip constraints.
        required_fields = ("destination", "duration_days", "num_people", "total_budget", "currency", "daily_focus")
        missing = [field for field in required_fields if field not in final_plan]
        if missing:
            raise ValueError("Planner JSON is missing required fields: " + ", ".join(missing))
        if not isinstance(final_plan["daily_focus"], list):
            raise ValueError("Planner JSON field 'daily_focus' must be a list.")

        log("Budget Agent", "Analyzing blueprint and using tools when needed")
        budget_input = f"Trip blueprint JSON:\n{json.dumps(final_plan, indent=2)}\n\nOriginal request:\n{trip_request}\n\nUse live tools when useful."
        final_budget, tool_logs = budget_agent.run(budget_input)

        log("Writer", "Writing the complete itinerary")
        writer_input = (f"Original request:\n{trip_request}\n\nBlueprint JSON:\n{json.dumps(final_plan, indent=2)}"
                        f"\n\nBudget analysis:\n{final_budget}\n\nTool results:\n{json.dumps(tool_logs, indent=2)}\n\nWrite the full itinerary.")
        final_itinerary, _ = writer.run(writer_input)

        log("Reviewer", f"Reviewing itinerary (round {iteration})")
        review_input = (f"Request:\n{trip_request}\n\nBlueprint JSON:\n{json.dumps(final_plan, indent=2)}"
                        f"\n\nBudget analysis:\n{final_budget}\n\nItinerary:\n{final_itinerary}\n\n"
                        "Check exact days, travelers, budget limit, practical timing and consistency. "
                        "Your response MUST start with exactly APPROVED if all checks pass, otherwise start with REVISE: "
                        "and list concrete corrections for the Planner. Do not approve an over-budget plan.")
        verdict, _ = reviewer.run(review_input)
        verdict = (verdict or "").strip()
        approved = verdict.upper().startswith("APPROVED")
        history.append({"iteration": iteration, "reviewer_verdict": verdict,
                        "is_approved": approved, "feedback": "" if approved else verdict})
        log("Reviewer", "APPROVED — final plan accepted" if approved else "REVISE — sending feedback to Planner",
            {"iteration": iteration, "verdict": verdict})
        if approved:
            break
        feedback = verdict

    return {"success": approved, "approval_status": "APPROVED",
            "iterations_completed": len(history),
            "history": history, "final_itinerary": final_itinerary,
            "final_plan": final_plan, "final_budget": final_budget}


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    key = os.getenv("GROQ_API_KEY") or input("Enter Groq API key: ").strip()
    request = input("Describe your trip (destination, days, people, budget): ").strip()
    if not request:
        raise SystemExit("A trip description is required.")
    outcome = orchestrate_trip_planning(request, key)
    print(outcome["final_itinerary"])
