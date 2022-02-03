import React from 'react';
import styled from 'styled-components';

// Styling for div encompassing all elements on the home page.
const TextDiv = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  overflow: scroll;
  margin-top: 10px;
`;

// Styling for the span containing the description of the application on the home page.
const Description = styled.span`
  width: 30vw;
  white-space: pre-line;
`;

// Home page descriptions of the model and query pages.
const modelDescription = 'Click the "Model" button to build a model based on the effects of game-playing on patients\n\n'
const queryDescription = 'Click the "Visualize" button to query patient data and access descriptive statistics\n\n'
const dashBoardDescription = 'Click the "Monitor" button to monitor patient health data over time'

/**
 * Component for the home page of the application.
 */
function Home(){
  return(
    <TextDiv>
      <h2> Welcome to AppEase </h2>
      <Description>
        {modelDescription}
        {queryDescription}
        {dashBoardDescription}
      </Description>
    </TextDiv>
  );
}

export default Home;
