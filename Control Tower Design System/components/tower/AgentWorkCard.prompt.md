One-line: the "what is the AI actually doing" card — use it wherever a progress bar alone would leave the supervisor guessing.

```jsx
<AgentWorkCard taskId="TSK-02" agent="be-dev" status="in-progress" elapsed="18 phút"
  title="BE: migration + model + service + tests"
  doing="Viết migration cho bảng release — unique (project_id, name)"
  target="app-be/migrations/003_release.py"
  steps={[{ label: 'Migration', state: 'doing' }, { label: 'Service + router', state: 'todo' }]}
  messages={[{ id: 'MSG-0060', from: 'be-dev', to: 'fe-dev', type: 'answer', body: 'chốt: trả code, FE map i18n' }]}
  waitingOn="backend-reviewer ký sau khi tests xanh" />
```

Keep `doing` concrete — a file, a rule, a decision being applied — never "đang xử lý".
