import 'react'
import { useState, useEffect } from 'react'
import { useApi } from '../utils/api'

export function MCQChallenge({challenge, showExplanation=false, onAnswerSubmit}) {
  const [selectedOption, setSelectedOption] = useState(null)
  const [shouldShowExplanation, setShouldShowExplanation] = useState(showExplanation)
  const {makeRequest} = useApi()

  // Reset state when challenge changes
  useEffect(() => {
    setSelectedOption(null)
    setShouldShowExplanation(showExplanation)
  }, [challenge?.id, showExplanation])

  const options = typeof challenge.options === "string"
    ? JSON.parse(challenge.options)
    : challenge.options

  const handleOptionSelect = async (index) => {
    if (selectedOption !== null) return;
    setSelectedOption(index)
    setShouldShowExplanation(true)
    
    // Submit answer to backend
    try {
      await makeRequest("submit-answer", {
        method: "POST",
        body: JSON.stringify({
          challenge_id: challenge.id,
          selected_answer_id: index
        })
      })
      onAnswerSubmit?.()
    } catch (err) {
      console.error("Failed to submit answer:", err)
    }
  }

  // handles highlighting red or greeen for answer
  // checks if you choose the right answer, wrong answer or dont choose anything
  const getOptionClass = (index) => {
    if (selectedOption === null) return "option"
    if (index === challenge.correct_answer_id) {
      return "option correct"
    }
    if (selectedOption === index && index !== challenge.correct_answer_id) {
      return "option incorrect"
    }

    return "option"
  }
  return <div className="challenge-display">
    <p><strong>Difficulty:</strong> {challenge.difficulty}</p>
    <p className="challenge-title">{challenge.title}</p>
    <div className="options">
      {options.map((option, index) => (
        <div
          className={getOptionClass(index)}
          key={index}
          onClick={() => handleOptionSelect(index)}
        >
          {option}
        </div>
      ))}
    </div>
    {shouldShowExplanation && selectedOption !== null && (
      <div className="explanation">
        <h4>Explanation</h4>
        <p>{challenge.explanation}</p>
      </div>
    )}
  </div>
}