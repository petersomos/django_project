import React, { useState, useEffect } from "react";
import "./QuizComponent.css";

const QuizComponent = () => {
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Fetch data from Django API
    fetch("https://django.somos-co.com/tensorflow-api/quiz/")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to fetch questions");
        }
        return response.json();
      })
      .then((data) => {
        setQuestions(data.questions);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching questions:", error);
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <div className="quiz-container">
      {questions.map((question, index) => (
        <div key={index} className="quiz-question">
          <h2>{question.text}</h2>
          <ul>
            {question.options.map((option, idx) => (
              <li key={idx}>
                <label>
                  <input
                    type="radio"
                    name={`question_${question.id}`}
                    value={option.id}
                  />
                  {option.text}
                </label>
              </li>
            ))}
          </ul>
        </div>
      ))}
      <button type="submit">Submit</button>
    </div>
  );
};

export default QuizComponent;
