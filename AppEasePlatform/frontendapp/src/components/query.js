import React, { useState } from 'react';
import styled from 'styled-components';
import Select from 'react-select';
import ModelButton from './model-page-button'
import DatePicker from './date-picker'

// Stying for div encompassing all other elements of the page.
const OuterDiv = styled.div`
  margin-top: 20px;
  display: inline-block;
  justify-content: center;
`;

// Stying for div encompassing query results and result title.
const ResultDiv = styled.div`
  width: 360px;
  height: 40vh;
  background-color: #DCDCDC;
  margin-left: 0;
  margin-right: auto;
  margin-top: 0;
  overflow: scroll;
`;

// Stying for element for displaying query results.
const ResultText = styled.p`
  text-align: left;
  margin: 10px 10px 10px 10px;
  overflow-wrap: break-word;
  white-space: pre-line;
`

// Styling for an individual horizontal subsection of the page.
const RowDiv = styled.div`
  display: flex;
  align-items: center;
  justify-content: center;
`

// Options for the query parameter selection dropdown.
const options = [
  { value: 'mean', label: 'Mean' },
  { value: 'median', label: 'Median' },
  { value: 'mode', label: 'Mode' },
  { value: 'variance', label: 'Variance'},
  { value: 'stdev', label: 'Standard Deviation'},
];

// Endpoint for Django app used for sending requests for data querying.
const BACKEND_QUERY = 'http://192.168.0.154:8000/api/query/'

/**
 * Component for the query page of the application.
 */
function Query(){
  // Stores/updates the query parameter selected by the user.
  const [selectedOption, setSelectedOption] = useState(null);
  // Store/updates the start and end dates for desired data.
  const [startDate, setStartDate] = useState();
  const [endDate, setEndDate] = useState();

  // Stores/updates whether a request from the network for query results is loading.
  const [loading, setLoading] = useState(false);

  // Stores/updates the results for the most recent query request.
  const [results, setResults] = useState(null);

  /**
   * Sends a request to the Django app to query the available patient data using
   * the specified parameter.
   */
  function request(){
    var start = startDate.toLocaleDateString().replaceAll("/", "-");
    var end = endDate.toLocaleDateString().replaceAll("/", "-");
    var url = BACKEND_QUERY + selectedOption + "/" + start + "/" + end + "/";
    setLoading(true);
    fetch(url, {
      method: 'GET',
    })
      .then(response => response.json())
      .then(data => {
        setResults(data.message)
        setLoading(false);
      }
      );
  }

  return (
    <OuterDiv>
      {/*section containing parameter dropdown and button for initiating data querying*/}
      <DatePicker startDate={startDate} setStartDate={setStartDate} endDate={endDate} setEndDate={setEndDate}/>
      <RowDiv>
        <div style={{width: "200px"}}>
          <Select
            menuPortalTarget={document.body}
            menuPosition={'fixed'}
            defaultValue={selectedOption}
            onChange={e => setSelectedOption(e.value)}
            options={options}
            placeholder={'Select parameter'}
          />
        </div>
        <ModelButton
          active={selectedOption && startDate && endDate}
          handleClick={request}
          label={"Query Data"}/>
      </RowDiv>

      {/*section for query results*/}
      <div style={{marginTop: "40px"}}>
        <h2 style={{textAlign: "left", marginBottom: "5px"}}>Query Results</h2>
        <ResultDiv>
          <ResultText>
            {
              (results && !loading)?
              results :
                (loading ?
                  <i> Fetching query results. </i> :
                  <i> Query result will show here. </i>
                )
            }
          </ResultText>
        </ResultDiv>
      </div>
    </OuterDiv>
  );
}

export default Query;
