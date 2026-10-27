---
type: Concept
id: 19_procedural_knowledge_improves_agentic_llm_workfl
title: "Procedural Knowledge Improves Agentic LLM Workflows (part 20/35)"
source: "Procedural Knowledge Improves Agentic LLM Workflows.pdf"
tags: [agentic, agents, context-engineering, memory, planning, prompt-engineering]

generated: { by: okf-enforcer/0.6, at: 2026-10-24T23:21:30Z }
---

Origin: Detroit
Destination: San Diego
Departure Date: 2022-03-05
Returning Date: 2022-03-07
Duration: 3 days
Budget: $3000
Traveler: solo
FlightSearch.run method:
- Inputs:
* Departure City (string)
* Destination City (string)
* Date (string in YYYY-MM-DD format)
- Expected Output:
* List of flight options (each containing flight number, departure/arrival
times, price, etc.),→
***NOTES END***
Your last response was:
***LAST RESPONSE START***
{
"observation": "We have read the tools specification which shows how to import
and use the Flights tool. To obtain flight options we need to write code
in solver.py that imports the Flights class, creates an instance, runs the
search for Detroit to San Diego on 2022-03-05, and prints the results. The
solver will then be executed and its stdout captured in output.txt for
later analysis.",
,→
,→
,→
,→
,→
"thought": "Next step is to write the described code into solver.py so that
the flight search is performed and results are printed. This will allow us
to later read output.txt and extract a departing flight number and cost.",
,→
,→
"action": {
"name": "Write",
"action_arg1": "solver.py",
"action_arg2": "from tools.Flights import Flights\n\ndef main():\n
FlightSearch = Flights()\n results = FlightSearch.run(\"Detroit\",
\"San Diego\", \"2022-03-05\")\n print(results)\n\nif __name__ ==
\"__main__\":\n main()\n"
,→
,→
,→
}
}
***LAST RESPONSE END***
The last ten commands executed were:
***LAST COMMAND START***
Verify
Read files/request.txt
Append files/notes.txt
Verify
Read files/tools_specification.txt
Append files/notes.txt
Verify
Read solver.py
Read files/tools_specification.txt
23
