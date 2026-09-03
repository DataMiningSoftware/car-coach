const BASE = '/api'

async function post(path, body) {
  const res = await fetch(BASE + path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}

export const askKnowledge = (car, question) => post('/knowledge', { car, question })
export const getMods = (car, goal, budget_rm, usage) =>
  post('/mods', { car, goal, budget_rm, usage })
export const getWorkshops = (need, location) => post('/workshops', { need, location })
export const visualize = (car, description) => post('/visualize', { car, description })

export async function uploadDocument(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(BASE + '/documents', { method: 'POST', body: form })
  if (!res.ok) throw new Error(await res.text())
  return res.json()
}
