"""Curated evidence input; HTTP availability is not factual verification."""
from .common import read
def select(used,topic_id=""):
 candidates=[t for t in read("data/topics.json") if t["id"] not in used and (not topic_id or t["id"]==topic_id)]
 if not candidates:raise RuntimeError("No unused evidence-reviewed topic; add a sourced packet")
 topic=candidates[0]
 for c in topic["claims"]:
  if c["kind"] not in ("fact","theory","myth") or not c["source_indices"] or any(i<0 or i>=len(topic["sources"]) for i in c["source_indices"]):raise ValueError("Unsourced claim")
 return topic
