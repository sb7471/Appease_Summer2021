import React, { useState } from 'react';
import styled from 'styled-components';
import Select from 'react-select';
import ModelButton from './model-page-button'
import FileSaver from 'file-saver';
import DatePicker from './date-picker'
import { getToken, getUser } from '../utils/common';

// Styling for div encompassing all other elements of the page.
const OuterDiv = styled.div`
  margin-top: 20px;
  display: inline-block;
  justify-content: left;
`;

// Styling for div encompassing query results and result title.
const ResultDiv = styled.div`
  width: 450px;
  height: 40vh;
  background-color: #DCDCDC;
  margin-left: 0;
  margin-right: auto;
  margin-top: 0;
  overflow: scroll;
`;

// Styling for element for displaying modeling results.
const ResultText = styled.p`
  text-align: left;
  margin: 10px 10px 10px 10px;
  overflow-wrap: break-word;
  white-space: pre-line;
`

// Styling for an individual horizontal subsection of the page.
const RowDiv = styled.span`
  display: flex;
  align-items: center;
  justify-content: center;
`

// Styling for the input element in which the user enters a name of a .txt file
// for saving results to.
const Input = styled.input`
  width: 250px;
  height: 25px;
  border-radius: 6px;
  marginRight: 20px;
`

// Options for the game selection dropdown.
const options = [
  { value: 'yes', label: 'Yes'},
  { value: 'no', label: 'No'},
];

// Endpoint for Django app used for sending requests for model buildling.
const BACKEND_MODEL = 'http://192.168.0.154:8000/api/model/'

const resultPlaceholder = 'Modeling results will show here.'

/**
 * Component for the model page of the application.
 */
function Model(){
  // Stores/updates the game selected by the user.
  const [selectedOption, setSelectedOption] = useState(null);
  // Store/updates the start and end dates for desired data.
  const [startDate, setStartDate] = useState();
  const [endDate, setEndDate] = useState();

  // Stores/updates whether a request from the network for query results is loading.
  const [loading, setLoading] = useState(false);
  // Stores/updates the results for the most recent built model.
  const [results, setResults] = useState(null);
  // Stores/updates the name of the txt file to save results to.
  const [downloadName, setDownloadName] = useState("");

  /**
   * Saves the results stored in results to a text file with a name
   * equal to the current downloadName.
   */
  function saveResults(){
    var data = results;
    if (!data){
      data = resultPlaceholder;
    }
    var blob = new Blob([data], {type: "text/plain;charset=utf-8"});
    FileSaver.saveAs(blob, downloadName);
  }

  /**
   * Sends a request to the Django app to build a model using health data
   * associated with playing of the specified game.
   */
  function request(){
    var start = startDate.toLocaleDateString().replaceAll("/", "-");
    var end = endDate.toLocaleDateString().replaceAll("/", "-");
    const token = getToken();
    const name = getUser();

    var url = BACKEND_MODEL + selectedOption + "/" + start + "/" + end + "/";
    setLoading(true);
    fetch(url, {
      method: 'GET',
    })
      .then(response => response.json())
      .then(data => {
          setResults(data.message);
          setLoading(false);
        }
      );
  }

  return (
    <OuterDiv>
      {/*section containing game dropdown and button for initiating model building*/}
      <DatePicker startDate={startDate} setStartDate={setStartDate} endDate={endDate} setEndDate={setEndDate}/>
      <RowDiv>
        <div style={{width: "200px"}}>
          <Select
            defaultValue={selectedOption}
            onChange={e => setSelectedOption(e.value)}
            options={options}
            placeholder={'Use intercept?'}
          />
        </div>
        <ModelButton
          active={selectedOption}
          handleClick={request}
          label={"Build Model"}/>
      </RowDiv>

      {/*section for modeling results*/}
      <div style={{marginTop: "30px", marginBottom: "30px"}}>
        <h2 style={{textAlign: "left", marginBottom: "5px"}}>Modeling Results</h2>
        <ResultDiv>
          <ResultText>
            {
              (results && !loading)?
              results :
                (loading ?
                  <i> Fetching query results. </i> :
                  <i> {resultPlaceholder} </i>
                )
            }
          </ResultText>
        </ResultDiv>
      </div>

      {/*section for specifying name of the download file and initiating result downloading*/}
      <RowDiv style={{marginTop: "10px"}}>
        <Input type="text" value={downloadName}  placeholder={"Enter a filename for downloaded data"} onChange={e => setDownloadName(e.target.value)} />
        <ModelButton active={true} handleClick={saveResults} label={"Download Data"}/>
      </RowDiv>
    </OuterDiv>
  );
}

export default Model;
