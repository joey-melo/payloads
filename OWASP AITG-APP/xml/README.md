## XML Payloads

I wanted to use the Burpsutie Extension [https://github.com/moha99sa/AI_Prompt_Fuzzer](https://github.com/moha99sa/AI_Prompt_Fuzzer) which consumes AI payloads in XML format. I loved the Payloads provided here but they were in yaml, so just wrote a short [script](./convert_prompts_to_xml.py) to convert YAML to XML with a little bit of context to generate payloads in XML format consumable by the above extension.

Also, sharing the final XML version of the payloads, I've tried and tested and works great with the above extension.

