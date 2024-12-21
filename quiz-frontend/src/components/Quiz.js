import React, { useState, useEffect } from "react";
import "../index.css"; 
import QuizSummary from './QuizSummary.js';

const Quiz = () => {
  const [questions, setQuestions] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [language, setLanguage] = useState("en");
  const [score, setScore] = useState(null); // Track quiz score
  const [totalQuestions, setTotalQuestions] = useState(0); // Total number of questions

  const handleLanguageChange = (e) => {
    setLanguage(e.target.value);
  };

  useEffect(() => {
    setLoading(true);
    fetch(`https://django.somos-co.com/tensorflow-api/quiz/?lang=${language}`)
      .then((response) => response.json())
      .then((data) => {
        setQuestions(data.questions || []);
        setTotalQuestions(data.questions?.length || 0);
      })
      .catch((error) => {
        console.error("Error fetching quiz data:", error);
      })
      .finally(() => setLoading(false));
  }, [language]);

  const handleAnswerChange = (questionId, optionId) => {
    setAnswers({ ...answers, [questionId]: optionId });
  };

  const handleNext = () => {
    if (currentIndex < questions.length - 1) {
      setCurrentIndex(currentIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentIndex > 0) {
      setCurrentIndex(currentIndex - 1);
    }
  };

  const handleSubmit = () => {
    console.log("Submitting answers:", answers);
    fetch("https://django.somos-co.com/tensorflow-api/quiz/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ answers }), // Ensure you are sending the `answers` object
    })
    .then((response) => {
        if (!response.ok) {
            throw new Error("Failed to fetch results");
        }
        return response.json();
    })
    .then((data) => {
        console.log("Server response:", data);
        if (data.message && data.score !== undefined) {
            setScore(data.score); // Save score
        } else {
            alert("Failed to fetch results");
        }
    })
    .catch((error) => {
        console.error("Submit error:", error);
        alert("Failed to fetch results");
    });
};


  const handleRestart = () => {
    setScore(null);
    setCurrentIndex(0);
    setAnswers({});
  };

  if (loading) {
    return <p>Loading...</p>;
  }

  if (score !== null) {
    // Show summary page
    return (
      <QuizSummary
        score={score}
        totalQuestions={totalQuestions}
        onRestart={handleRestart}
      />
    );
  }

  if (questions.length === 0) {
    return <p>No questions available.</p>;
  }

  const currentQuestion = questions[currentIndex];

  return (
    <div className="quiz-container">
      <h1>Quiz</h1>
      <label>
        Select Language:
        <select value={language} onChange={handleLanguageChange}>
          <option value="en">English</option>
          <option value="de">German</option>
          <option value="fr">French</option>
          <option value="hu">Hungarian</option>
          <option value="sk">Slovak</option>
        </select>
      </label>
      {currentQuestion && (
        <div>
          <h2>{currentQuestion.text}</h2>
          <ul>
            {currentQuestion.options.map((option) => (
              <li key={option.id}>
                <label>
                  <input
                    type="radio"
                    name={`question_${currentQuestion.id}`}
                    value={option.id}
                    checked={answers[currentQuestion.id] === option.id || false}
                    onChange={() =>
                      handleAnswerChange(currentQuestion.id, option.id)
                    }
                  />
                  {option.text}
                </label>
              </li>
            ))}
          </ul>
        </div>
      )}
      <div className="quiz-nav-buttons">
        <button onClick={handlePrevious} disabled={currentIndex === 0}>
          Previous
        </button>
        <button
          onClick={
            currentIndex === questions.length - 1 ? handleSubmit : handleNext
          }
        >
          {currentIndex === questions.length - 1 ? "Submit" : "Next"}
        </button>
      </div>
    </div>
  );
};

export default Quiz;
