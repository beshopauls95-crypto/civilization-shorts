"""Original grounded editorial fallback. No live language model configured."""
def generate(topic):
 scenes=topic["narration"]
 words=len(" ".join(scenes).split())
 if not 65<=words<=150:raise ValueError("Episode narration outside Shorts word budget")
 return {"title":topic["title"],"scenes":scenes,"generator":"grounded_editorial","review_required":True,"description":topic["title"]+"\nمشاهد تخيلية مولدة بالذكاء الاصطناعي وتعليق صوتي آلي.\n"+"\n".join(s["url"] for s in topic["sources"])+"\n#حكاوى_التاريخ #تاريخ #Shorts","tags":["حكاوى التاريخ","تاريخ","Shorts"]}
