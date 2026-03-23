import os
import sys
import unittest


sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

from cnbc_fetcher import (
    CNBC_QUOTES,
    CNBC_FX_SYMBOLS,
    extract_cnbc_exchange_rates,
    fetch_cnbc_data,
)


def print_live_exchange_snapshot(quotes, rates):
    print("\nCNBC live FX endpoints:")
    for symbol in CNBC_FX_SYMBOLS:
        print(f"{symbol}: {CNBC_QUOTES[symbol]['url']}")
    print("Live exchange rates:")
    print(f"USD/KRW: {rates.usd_krw:.4f}")
    print(f"USD/JPY: {rates.usd_jpy:.4f}")
    print(f"EUR/USD: {rates.eur_usd:.4f}")
    print(f"USD/CNY: {rates.usd_cny:.4f}")
    print(f"JPY/KRW (100 JPY): {(rates.usd_krw / rates.usd_jpy) * 100:.4f}")
    print(f"EUR/KRW: {rates.usd_krw * rates.eur_usd:.4f}")
    print(f"CNY/KRW: {rates.usd_krw / rates.usd_cny:.4f}")
    print("Raw CNBC FX quotes:")
    for symbol in CNBC_FX_SYMBOLS:
        quote = quotes[symbol]
        print(
            f"{symbol}: price={quote.price:.4f}, "
            f"change={quote.change:+.4f}, "
            f"change_pct={quote.change_pct:+.4f}%"
        )


@unittest.skipUnless(
    os.environ.get("RUN_LIVE_SMOKE_TESTS") == "1",
    "Set RUN_LIVE_SMOKE_TESTS=1 to hit the live CNBC FX quote pages.",
)
class CnbcExchangeRateSmokeTests(unittest.TestCase):
    def test_live_cnbc_fx_pages_return_expected_rates(self):
        quotes = fetch_cnbc_data(list(CNBC_FX_SYMBOLS))

        self.assertEqual(set(quotes), set(CNBC_FX_SYMBOLS))
        for symbol in CNBC_FX_SYMBOLS:
            self.assertGreater(quotes[symbol].price, 0)

        mapped_rates = extract_cnbc_exchange_rates(quotes)

        self.assertAlmostEqual(mapped_rates.usd_krw, quotes["KRW="].price)
        self.assertAlmostEqual(mapped_rates.usd_jpy, quotes["JPY="].price)
        self.assertAlmostEqual(mapped_rates.usd_cny, quotes["CNY="].price)
        self.assertAlmostEqual(mapped_rates.eur_usd, quotes["EUR="].price)

        print_live_exchange_snapshot(quotes, mapped_rates)


if __name__ == "__main__":
    unittest.main(verbosity=2)
