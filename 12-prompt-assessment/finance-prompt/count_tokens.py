"""Counts tokens in the original and optimized prompts."""

import tiktoken
from myprompts import FINANCE_PROMPT, FINANCE_PROMPT_OPTIMIZED

# Use gpt-4o-mini encoder (same as gpt-4o family)
encoder = tiktoken.encoding_for_model("gpt-4o-mini")

# Use sample placeholders so .format() works
sample_context = "Sample context placeholder for token counting."
sample_query   = "Sample user query."

original_filled  = FINANCE_PROMPT.format(context=sample_context, user_query=sample_query)
optimized_filled = FINANCE_PROMPT_OPTIMIZED.format(context=sample_context, user_query=sample_query)

orig_tokens = len(encoder.encode(original_filled))
opt_tokens  = len(encoder.encode(optimized_filled))

saving_tokens = orig_tokens - opt_tokens
saving_pct    = (saving_tokens / orig_tokens) * 100

print("=" * 60)
print("PROMPT TOKEN COMPARISON (gpt-4o-mini encoding)")
print("=" * 60)
print(f"Original prompt tokens     : {orig_tokens}")
print(f"Optimized prompt tokens    : {opt_tokens}")
print(f"Tokens saved per call      : {saving_tokens}")
print(f"Percentage reduction       : {saving_pct:.1f}%")
print()
print("Cost projection (gpt-4o-mini input @ $0.15 per 1M tokens):")
print(f"  Saving per 1,000 calls   : ${(saving_tokens * 1000 * 0.15 / 1_000_000):.4f}")
print(f"  Saving per 1,000,000 calls: ${(saving_tokens * 1_000_000 * 0.15 / 1_000_000):.2f}")
print("=" * 60)
