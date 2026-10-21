Original operator files belong here: state-A.jsonl / traces-A.csv through E.
Lots A to D ran on 21 October 2026 (state-A to state-D); lot E pending. Invalid-key runs of lot A are kept in failed-access/, outside consolidation. Do not create fake empty state records.
Keep state files across resumptions and import them without editing their contents.
Only state-*.jsonl files enter td1.py consolidation; retain the original CSVs too.
