import { useState } from 'react'
import {
  askKnowledge,
  getMods,
  getWorkshops,
  uploadDocument,
  visualize,
} from './api.js'

const TABS = ['Ask', 'Mods', 'Documents', 'Workshops', 'Visualize']

export default function App() {
  const [tab, setTab] = useState('Ask')
  const [car, setCar] = useState({ make: '', model: '', year: '' })

  return (
    <div className="app">
      <header>
        <h1>car-coach</h1>
        <p className="subtitle">Your AI companion for everything about your car (Malaysia)</p>
      </header>

      <section className="car-form">
        <input placeholder="Make (e.g. Perodua)" value={car.make}
          onChange={(e) => setCar({ ...car, make: e.target.value })} />
        <input placeholder="Model (e.g. Myvi)" value={car.model}
          onChange={(e) => setCar({ ...car, model: e.target.value })} />
        <input placeholder="Year (e.g. 2022)" value={car.year}
          onChange={(e) => setCar({ ...car, year: e.target.value })} />
      </section>

      <nav className="tabs">
        {TABS.map((t) => (
          <button key={t} className={tab === t ? 'active' : ''} onClick={() => setTab(t)}>
            {t}
          </button>
        ))}
      </nav>

      {tab === 'Ask' && <AskTab car={car} />}
      {tab === 'Mods' && <ModsTab car={car} />}
      {tab === 'Documents' && <DocsTab />}
      {tab === 'Workshops' && <WorkshopsTab />}
      {tab === 'Visualize' && <VisualizeTab car={car} />}
    </div>
  )
}

function AskTab({ car }) {
  const [question, setQuestion] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function submit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      setResult(await askKnowledge(car, question))
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="panel">
      <form onSubmit={submit}>
        <input
          className="wide"
          placeholder="e.g. What are the specs, and is it reliable?"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button type="submit" disabled={loading || !question}>
          {loading ? 'Thinking…' : 'Ask'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="answer">
          <p>{result.answer}</p>
          {result.sources?.length > 0 && (
            <small>Sources: {result.sources.join(', ')}</small>
          )}
        </div>
      )}
    </div>
  )
}

function ModsTab({ car }) {
  const [goal, setGoal] = useState('')
  const [budget, setBudget] = useState('')
  const [usage, setUsage] = useState('street')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function submit(e) {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      setResult(await getMods(car, goal, budget ? Number(budget) : null, usage))
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="panel">
      <form onSubmit={submit}>
        <input className="wide" placeholder="Goal (e.g. more horsepower, better handling)"
          value={goal} onChange={(e) => setGoal(e.target.value)} />
        <input placeholder="Budget (RM)" value={budget}
          onChange={(e) => setBudget(e.target.value)} />
        <select value={usage} onChange={(e) => setUsage(e.target.value)}>
          <option value="street">Street</option>
          <option value="track">Track</option>
          <option value="offroad">Off-road</option>
        </select>
        <button type="submit" disabled={loading || !goal}>
          {loading ? 'Thinking…' : 'Get advice'}
        </button>
      </form>
      {error && <p className="error">{error}</p>}
      {result && (
        <div>
          {result.summary && <p>{result.summary}</p>}
          {result.mods?.map((m, i) => (
            <div className="card" key={i}>
              <h3>{m.name} <span className="badge">{m.category}</span></h3>
              <p><strong>Gains:</strong> {m.expected_gains}</p>
              <p><strong>Cost:</strong> {m.cost_rm} · <strong>Difficulty:</strong> {m.difficulty}</p>
              <p><strong>Legality (MY):</strong> {m.legality_my}</p>
              {m.caveats && <p className="muted">{m.caveats}</p>}
            </div>
          ))}
          {result.legal_disclaimer && <p className="muted">⚠ {result.legal_disclaimer}</p>}
        </div>
      )}
    </div>
  )
}

function DocsTab() {
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function upload(e) {
    const file = e.target.files[0]
    if (!file) return
    setLoading(true)
    setError('')
    try {
      setResult(await uploadDocument(file))
    } catch (err) {
      setError(String(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="panel">
      <p>Upload a vehicle document (JPJ grant, insurance, Puspakom report). PII is redacted before extraction.</p>
      <input type="file" accept=".pdf,.png,.jpg,.jpeg" onChange={upload} />
      {loading && <p>Extracting…</p>}
      {error && <p className="error">{error}</p>}
      {result && (
        <div className="answer">
          {result.masked && <small>PII redacted ✓</small>}
          {result.fields && Object.keys(result.fields).length > 0 && (
            <pre>{JSON.stringify(result.fields, null, 2)}</pre>
          )}
          <pre>{result.text}</pre>
        </div>
      )}
    </div>
  )
}

function WorkshopsTab() {
  const [need, setNeed] = useState('')
  const [location, setLocation] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  async function submit(e) {
    e.preventDefault()
    setError('')
    try {
      setResult(await getWorkshops(need, location))
    } catch (err) {
      setError(String(err))
    }
  }

  return (
    <div className="panel">
      <form onSubmit={submit}>
        <input className="wide" placeholder="Need (e.g. vintage restoration, performance tuning)"
          value={need} onChange={(e) => setNeed(e.target.value)} />
        <input placeholder="Location (e.g. Shah Alam)" value={location}
          onChange={(e) => setLocation(e.target.value)} />
        <button type="submit" disabled={!need}>Find workshops</button>
      </form>
      {error && <p className="error">{error}</p>}
      {result && result.map((w, i) => (
        <div className="card" key={i}>
          <h3>{w.name}</h3>
          <p>{w.specialty} · {w.location}{w.rating ? ` · ⭐ ${w.rating}` : ''}</p>
        </div>
      ))}
    </div>
  )
}

function VisualizeTab({ car }) {
  const [description, setDescription] = useState('')
  const [result, setResult] = useState(null)
  const [error, setError] = useState('')

  async function submit(e) {
    e.preventDefault()
    setError('')
    try {
      setResult(await visualize(`${car.make} ${car.model}`, description))
    } catch (err) {
      setError(String(err))
    }
  }

  return (
    <div className="panel">
      <p>Imagine what your car could look like — describe your idea in your own words.</p>
      <form onSubmit={submit}>
        <input className="wide" placeholder="e.g. matte grey wrap, gold rims, lowered"
          value={description} onChange={(e) => setDescription(e.target.value)} />
        <button type="submit" disabled={!description}>Generate</button>
      </form>
      {error && <p className="error">{error}</p>}
      {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
    </div>
  )
}
