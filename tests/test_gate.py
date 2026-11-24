from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
import copy, json, sys, importlib.util
spec = importlib.util.spec_from_file_location("gate", str(ROOT / "skills/setup/templates/repo/.github/harness/gate.py"))
g = importlib.util.module_from_spec(spec); spec.loader.exec_module(g)
policy = json.load(open(str(ROOT / "skills/setup/templates/repo/.github/harness/policy.json")))
policy_on = dict(policy, mode="on")
pr = {"number": 7, "state": "OPEN", "isDraft": False, "labels": [{"name": "claude-auto"}],
      "author": {"login": "app/github-actions"}, "headRefName": "claude/issue-3", "headRefOid": "abc",
      "body": "変更しました\n\nCloses #3", "changedFiles": 1, "additions": 5, "deletions": 1,
      "files": [{"path": "index.html", "additions": 5, "deletions": 1}]}
review = {"verdict": "approve", "risk": "low", "findings": [{"severity": "minor"}], "criteria": [{"text": "a", "met": True}]}
ok = dict(checks={"result": "success"}, review=review, issue={"author_association": "OWNER"}, run={"head_sha": "abc"})
def ev(p=policy_on, prx=pr, **kw):
    a = dict(ok); a.update(kw); return g.evaluate(p, prx, a["checks"], a["review"], a["issue"], a["run"])
def mod(**kw):
    x = copy.deepcopy(pr); x.update(kw); return x
cases = [
  ("all good on", ev(), True),
  ("shadow never merges", ev(p=policy), False),
  ("off never merges", ev(p=dict(policy, mode="off")), False),
  ("bogus mode -> off", ev(p=dict(policy, mode="yes")), False),
  ("no label -> not applies", ev(prx=mod(labels=[])), False),
  ("hold label", ev(prx=mod(labels=[{"name":"claude-auto"},{"name":"hold"}])), False),
  ("human author", ev(prx=mod(author={"login":"someone"})), False),
  ("wrong branch", ev(prx=mod(headRefName="feature/x")), False),
  ("sha changed", ev(run={"head_sha":"zzz"}), False),
  ("no closes", ev(prx=mod(body="hi")), False),
  ("external issue author", ev(issue={"author_association":"NONE"}), False),
  ("missing issue info", ev(issue={}), False),
  ("checks failed", ev(checks={"result":"failure"}), False),
  ("checks missing", ev(checks={}), False),
  ("review missing (fail closed)", ev(review={}), False),
  ("request changes", ev(review=dict(review, verdict="request_changes")), False),
  ("medium risk", ev(review=dict(review, risk="medium")), False),
  ("major finding", ev(review=dict(review, findings=[{"severity":"major"}])), False),
  ("unmet criteria", ev(review=dict(review, criteria=[{"text":"a","met":False}])), False),
  ("empty criteria", ev(review=dict(review, criteria=[])), False),
  ("too many files", ev(prx=mod(changedFiles=11)), False),
  ("too many lines", ev(prx=mod(additions=400)), False),
  ("truncated file list", ev(prx=mod(changedFiles=3)), False),
  ("workflow touched", ev(prx=mod(files=[{"path":".github/workflows/x.yml"}])), False),
  ("policy touched", ev(prx=mod(files=[{"path":".github/harness/policy.json"}])), False),
  ("root .env touched", ev(prx=mod(files=[{"path":".env"}])), False),
  ("nested .env touched", ev(prx=mod(files=[{"path":"app/.env.local"}])), False),
  ("CLAUDE.md touched", ev(prx=mod(files=[{"path":"CLAUDE.md"}])), False),
  ("check.sh touched", ev(prx=mod(files=[{"path":"scripts/check.sh"}])), False),
  ("lockfile touched", ev(prx=mod(files=[{"path":"package-lock.json"}])), False),
  ("closed PR", ev(prx=mod(state="CLOSED")), False),
  ("draft PR", ev(prx=mod(isDraft=True)), False),
]
bad = 0
for name, d, want in cases:
    got = d["merge"]
    if got != want: bad += 1; print("FAIL", name, json.dumps(d, ensure_ascii=False)[:300])
print(f"{len(cases)-bad}/{len(cases)} passed")
# eligible in shadow should be True
assert ev(p=policy)["eligible"] is True
assert "練習モード" in g.render(ev(p=policy))
assert "人の確認が必要" in g.render(ev(prx=mod(files=[{"path":".github/workflows/x.yml"}])))
assert g.render(ev(prx=mod(labels=[]))) == ""
sys.exit(1 if bad else 0)
