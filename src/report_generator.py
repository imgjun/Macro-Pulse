import base64
import io

import matplotlib
import matplotlib.pyplot as plt
from jinja2 import Environment, FileSystemLoader

from report_format_config import get_mode_format, load_report_format_config

# Use Agg backend for non-interactive environments
matplotlib.use("Agg")


def generate_sparkline(history):
    """
    Generates a sparkline image as a base64 string.
    """
    plt.figure(figsize=(2, 0.5))
    plt.plot(
        history,
        color="#2ecc71" if history[-1] >= history[0] else "#e74c3c",
        linewidth=2,
    )
    plt.axis("off")
    plt.tight_layout(pad=0)

    img = io.BytesIO()
    plt.savefig(img, format="png", transparent=True)
    img.seek(0)
    plt.close()

    return base64.b64encode(img.getvalue()).decode("utf-8")


def generate_html_report(data, template_dir="src/templates"):
    """
    Generates the HTML report using Jinja2.
    """
    for category, items in data.items():
        for item in items:
            if len(item.get("history", [])) > 1:
                item["sparkline"] = generate_sparkline(item["history"])
            else:
                item["sparkline"] = ""

            if item.get("price") is not None:
                if "KRW" in item["name"] or "Yen" in item["name"]:
                    item["price_str"] = f"{item['price']:,.2f}"
                elif (
                    "Bond" in item["name"]
                    or "Treasury" in item["name"]
                    or "Year" in item["name"]
                ):
                    item["price_str"] = f"{item['price']:.3f}"
                else:
                    item["price_str"] = f"{item['price']:,.2f}"
            else:
                item["price_str"] = ""

            if item.get("change") is not None:
                item["change_str"] = f"{item['change']:+,.2f}"
                item["change_pct_str"] = f"{item['change_pct']:+,.2f}%"
                item["color_class"] = (
                    "positive"
                    if item["change"] > 0
                    else "negative"
                    if item["change"] < 0
                    else "neutral"
                )
            else:
                item["change_str"] = ""
                item["change_pct_str"] = ""
                item["color_class"] = "neutral"

    env = Environment(loader=FileSystemLoader(template_dir))
    template = env.get_template("report.html")
    return template.render(data=data)


def generate_telegram_summary(data, mode="Global", format_config=None):
    """
    Generates a text summary for Telegram based on the configured market mode.
    """

    def _format_line(item):
        price = item.get("price")
        change_pct = item.get("change_pct")

        if price is None:
            return f"{item['name']}: N/A"

        if (
            "KRW" in item["name"]
            or "Yen" in item["name"]
            or item["name"]
            in [
                "KOSPI",
                "KOSDAQ",
                "Nikkei 225",
                "Hang Seng",
                "Shanghai Composite",
                "Bitcoin",
                "Gold",
                "Silver",
                "S&P 500",
                "Nasdaq",
                "Euro Stoxx 50",
            ]
        ):
            price_str = f"{price:,.2f}"
        elif (
            "Bond" in item["name"]
            or "Treasury" in item["name"]
            or "Year" in item["name"]
        ):
            price_str = f"{price:.3f}"
        else:
            price_str = f"{price:,.2f}"

        if change_pct is not None and change_pct != 0:
            change_str = f"({change_pct:+,.2f}%)"
            return f"{item['name']}: {price_str} {change_str}"

        return f"{item['name']}: {price_str}"

    def get_items(category, names):
        found = []
        source_list = data.get(category, [])
        for name in names:
            for item in source_list:
                if item["name"] == name:
                    found.append(item)
                    break
        return found

    mode_format = get_mode_format(mode, format_config or load_report_format_config())
    sections = mode_format.get("summary_sections", [])

    lines = []
    for index, section in enumerate(sections):
        lines.append(f"[{section['title']}]")
        for item in get_items(section["category"], section["items"]):
            lines.append(_format_line(item))
        if index < len(sections) - 1:
            lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    pass
