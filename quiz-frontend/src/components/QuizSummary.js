import React from 'react';

const QuizSummary = ({ score, totalQuestions, onRestart }) => {
  return (
    <div className="quiz-summary">
      <h1>Quiz Summary</h1>
      <p>
        You scored <strong>{score}</strong> out of <strong>{totalQuestions}</strong>.
      </p>
      <button onClick={onRestart}>Retake Quiz</button>
    </div>
  );
};

export default QuizSummary;
