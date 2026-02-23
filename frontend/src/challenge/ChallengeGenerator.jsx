import 'react'
import {useState, useEffect, useCallback} from 'react'
import {MCQChallenge} from './MCQChallenge.jsx'
import {useApi} from '../utils/api.js' 

export function ChallengeGenerator() {
  // some of these consts are just a base template, can add abunch of other states that i can adjust later
  const [challenge, setChallenge] = useState(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)
  const [difficulty, setDifficulty] = useState('easy')
  const [quota, setQuota] = useState(null)
  const [stats, setStats] = useState(null)
  const {makeRequest} = useApi()

  const fetchQuota = useCallback(async () => {
    try {
        const data = await makeRequest("quota")
        setQuota(data)
    } catch (err) {
        console.log(err)
    }
  }, [makeRequest])

  const fetchStats = useCallback(async () => {
    try {
        const data = await makeRequest("stats")
        setStats(data)
    } catch (err) {
        console.log(err)
    }
  }, [makeRequest])

  useEffect(() => {
    fetchQuota()
    fetchStats()
  }, [fetchQuota, fetchStats])

  const generateChallenge = async () => {
    setIsLoading(true)
    setError(null)

    try {
      const data = await makeRequest("generate-challenge", {
        method: "POST",
        body: JSON.stringify({difficulty})
        }
      )
      setChallenge(data)
      fetchQuota()
      fetchStats()
    } catch (err) {
      setError(err.message || "Failed to generate challenge.")
    } finally {
      setIsLoading(false)
    }
  }

  const getNextResetTime = () => {
    if (!quota?.last_reset_date) return null
    const resetDate = new Date(quota.last_reset_date)
    resetDate.setHours(resetDate.getHours() + 24)
    return resetDate
  }

  return <div className="challenge-container">
    <h2>Coding Challenge</h2>

    {(quota || stats) && (
      <div className="quota-and-stats">
        {quota && (
          <div className="quota-display">
            <p>Challenges remaining today: {quota.quota_remaining}</p>
            {quota.last_reset_date ? (
              <p>Next reset: {getNextResetTime()?.toLocaleString?.() ?? ""}</p>
            ) : (
              <p>Next reset: 24 hours after your first challenge today</p>
            )}
          </div>
        )}
        {stats && (
          <div className="stats-display">
            <p className="stats-title">Your stats</p>
            <p>Total attempts: <strong>{stats.total_attempts}</strong></p>
            <p>Correct: <strong>{stats.total_correct}</strong> · Incorrect: <strong>{stats.total_incorrect}</strong></p>
            <p>Accuracy: <strong>{stats.accuracy_pct}%</strong></p>
            <p className="stats-streaks">
              Current streak: <strong>{stats.current_streak}</strong> · Best streak: <strong>{stats.best_streak}</strong>
            </p>
          </div>
        )}
      </div>
    )}
    <div className="difficulty-selector">
      <label htmlFor="difficulty">Select Difficulty</label>
      <select 
        id="difficulty"
        value={difficulty}
        onChange={(e)=>setDifficulty(e.target.value)}
        disabled={isLoading}
      >
        <option value="easy">Easy</option>
        <option value="medium">Medium</option>
        <option value="hard">Hard</option>
      </select>
    </div>

    <button
      onClick={generateChallenge}
      disabled={false} //isLoading || quota?.quota_remaining === 0
      className="generate-button"
    >
      {isLoading ? "Generating..." : "Generate Challenge"}
    </button>

    {error && <div className="error-message">
      <p>{error}</p>
    </div>}

    {challenge && <MCQChallenge challenge={challenge} onAnswerSubmit={fetchStats} />}
  </div>
}