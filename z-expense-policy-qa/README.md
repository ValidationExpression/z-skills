# z-expense-policy-qa

`z-expense-policy-qa` 是由 `z-grounded-source-qa` 生成的自包含制度核对 Skill

它演示了怎样把一份报销制度变成可以回答“能不能报、能报多少、缺什么材料、超标怎么办、依据哪一条”的专用 Skill

## 内置资料

- `reimbursement-policy-demo.md`

资料位于 `references/corpus/`，校验信息位于 `references/source-manifest.json`

当前“星河科技”制度为虚构示例。真实使用前，把 `references/corpus/` 替换成公司的有效报销制度、差旅标准、FAQ 和审批矩阵，并同步更新来源说明

## 使用

把整个目录放入 Agent 的 Skills 目录，随后直接提问与 报销制度问答助手 相关的问题

回答前会运行 `scripts/search_evidence.py`，以多表达式检索完整段落，并保留来源位置

三组实测问答见 [examples/golden-answers.md](examples/golden-answers.md)

运行验证：

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## 继续定制

1. 修改 `references/profile.md`，写清角色、语气、可靠性和边界
2. 替换或追加 `references/corpus/` 内资料
3. 更新 `evals/evals.json`，加入真实问题和验收标准
4. 运行代表性问答，检查结论、出处、推断和资料缺口
