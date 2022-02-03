import React from 'react';
import DayPickerInput from 'react-day-picker/DayPickerInput';
import 'react-day-picker/lib/style.css';
import styled from 'styled-components';

// Styling for div encompassing a DayPickerInput.
const PickerDiv = styled.div`
  display: inline-block;
  margin-right: 6px;
  margin-left: 6px;
  margin-bottom: 10px;
`;

/**
 * Component for selecting a date range.
 * @param {object} props Component props
 * @param {string} props.startDate The currently-selected start date on the page containing the component.
 * @param {string} props.endDate The currently-selected end date on the page containing the component.
 * @param {function} props.setStartDate The function to change the currently-selected start date.
 * @param {function} props.setEndDate The function to change the currently-selected end date.
 */
function DatePicker(props){

  // Styling for individual DayPickerInput.
  const pickerStyle = {
    height: 20,
    width: 165,
    borderColor: "#DCDCDC",
    borderRadius: 8
  };

  return(
    <div>
      <PickerDiv>
        {/* start date picker */}
        <DayPickerInput
          value={props.startDate}
          placeholder={"Select start date"}
          onDayChange={props.setStartDate}
          dayPickerProps={{
            disabledDays: {after: props.endDate},
          }}
          inputProps={{
            style: pickerStyle
          }}
        />
      </PickerDiv>
      <PickerDiv>
        {/* end date picker */}
        <DayPickerInput
          value={props.endDate}
          placeholder={"Select end date"}
          onDayChange={props.setEndDate}
          dayPickerProps={{
            disabledDays: {before: props.startDate},
          }}
          inputProps={{
            style: pickerStyle
          }}
        />
      </PickerDiv>
    </div>
  );
}

export default DatePicker;
