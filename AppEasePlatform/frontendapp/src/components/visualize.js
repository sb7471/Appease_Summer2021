import React, { useState } from 'react';
import styled from 'styled-components';
import Select from 'react-select';
import ModelButton from './model-page-button';

// Stying for div encompassing all other elements of the page.
const OuterDiv = styled.div`
  margin-top: 20px;
  display: inline-block;
  justify-content: center;
`;

// Stying for element for displaying visualization page text.
const ResultText = styled.div`
  text-align: left;
  margin: 10px 10px 10px 0px;
  overflow-wrap: break-word;
  width: 360px;
  margin-left: 0;
  margin-right: auto;
  margin-top: 0;
  overflow: scroll;
`

// Styling for an individual horizontal subsection of the page.
const RowDiv = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
`

// Options for the visualization feature selection dropdown.
const feature_options = [
  { value: 'distance(miles)', label: 'Distance' },
  { value: 'steps', label: 'Steps' },
  { value: 'heart_rate', label: 'Heart Rate' },
  { value: 'active_calories_burned', label: 'Calories Burned'},
];

// Options for the game selection dropdown.
const game_options = [
  { value: 'Angry-Birds', label: 'Angry Birds' },
  { value: 'Clash-of-Clans', label: 'Clash of Clans' },
  { value: 'Brawl-Stars', label: 'Brawl Stars' },
  { value: 'Injustice-2', label: 'Injustice 2' },
  { value: 'Catan', label: 'Catan' },
];

// Endpoint for Django app used for sending requests for visualizations.
const BACKEND_VISUALIZE = 'http://192.168.0.154:8000/api/visualize/'

/**
 * Component for the visualization page of the application.
 */
function Visualize(){
  const [selectedGame, setSelectedGame] = useState(null);
  // Stores/updates the visualization feature selected by the user.
  const [selectedOption, setSelectedOption] = useState(null);

  // Stores/updates the results for the most recent visualization received.
  const [results, setResults] = useState(null);

  /**
   * Sends a request to the Django app to create a visualization using the
   * specified feature.
   */
  function request(){
    var url = BACKEND_VISUALIZE + selectedGame + "/" + selectedOption + "/";
    fetch(url, {
      method: 'GET',
    })
      .then(response => response.blob())
      .then(image => {
          // Remove local image blob if a new visualization was created.
          if (results){
            URL.revokeObjectURL(results);
          }
          var imageURL = URL.createObjectURL(image);
          setResults(imageURL);
        }
      );
  }

  return (
    <OuterDiv>
      {/*section containing feature dropdown and button for initiating visualization*/}
      <RowDiv>
        <div style={{width: "250px"}}>
          <Select
            menuPortalTarget={document.body}
            menuPosition={'fixed'}
            defaultValue={selectedGame}
            onChange={e => setSelectedGame(e.value)}
            options={game_options}
            placeholder={'Select game'}
          />
        </div>
      </RowDiv>

      <RowDiv style={{marginTop: "10px"}}>
        <div style={{width: "200px"}}>
          <Select
            menuPortalTarget={document.body}
            menuPosition={'fixed'}
            defaultValue={selectedOption}
            onChange={e => setSelectedOption(e.value)}
            options={feature_options}
            placeholder={'Select feature'}
          />
        </div>
        <ModelButton
          active={selectedOption && selectedGame}
          handleClick={request}
          label={"Visualize"}/>
      </RowDiv>

      {/*section for visualization results*/}
      <div style={{marginTop: "20px"}}>
        <h2 style={{textAlign: "left", marginBottom: "5px"}}>Visualization Results</h2>
        {results?
          <img src={results} alt="Visual" width="360px" />
          :
          <ResultText>
            <i> Requested visualization will show here. </i>
          </ResultText>
        }
      </div>
    </OuterDiv>
  );
}

export default Visualize;
