# Gemini Live compatibility patch

The initial test uses Home Assistant 2026.10.0 and inspects
`matt123p/ha-gemini-live` v1.0.9, commit
`d4ad0e523eca92f1c395e82da14d6da0fafd71be`.

On that HA release `APIInstance.async_call_tool` returns a `ToolResult` object.
The inspected voice integration passes it through `_validate_tool_results`
unchanged into `google.genai.types.FunctionResponse(response=...)`. Google GenAI
2.21.0 requires a dictionary there and rejects the object with a validation error.
This affects home tools as well as Chan expressions.

We reproduced the rejection locally without a provider key. The included patch
unwraps successful results into `data` and preserves failed results as an
`error` dictionary. The existing recursive conversion still handles nested
results and dates. Both native audio and typed conversation paths use this helper.

## Developer reproduction only

This is not the user installation path. Install Chan through HACS and use a
working Assist pipeline. A compatible live backend delivered through HACS is
still needed; do not manually patch HA files as part of normal installation.

To reproduce the known compatibility fix on a development computer:

```sh
git clone https://github.com/matt123p/ha-gemini-live.git
git -C ha-gemini-live checkout d4ad0e523eca92f1c395e82da14d6da0fafd71be
git -C ha-gemini-live apply ../chan-home-assistant/patches/ha-gemini-live-tool-results.patch
```

The checkout is for local compatibility testing. It is not installed into HA
by these commands. An upstream release must include a compatible serializer
before recommending it as the normal HACS installation path.

The patch is against the exact revision above. Do not apply it blindly to a
different release. It changes result serialization only, not audio transport,
provider authentication, session timing, or interruption support.

## Reproduce the serializer check

Using the HA test environment with `google-genai==2.21.0` installed:

```sh
python tools/check_live_compat.py ../ha-gemini-live/custom_components/gemini_live/stt.py
```

The check executes only the patched pure conversion helper and validates success,
error, nested results, and SDK serialization. It makes no cloud requests and
does not establish working voice conversation on the robot.

See [THIRD_PARTY.md](../THIRD_PARTY.md) and
[the preserved upstream MIT notice](../LICENSES/ha-gemini-live-MIT.txt).
