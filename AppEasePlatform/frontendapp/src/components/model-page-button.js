import React from 'react';
import styled from 'styled-components';

// Styling for the button.
const Button = styled.button`
  background-color: ${props => props.disabled? '#C4C4C4' : '#590083'};
  color: ${props => props.disabled? '#9E9E9E': 'white'};
  border-radius: 12px;
  border: black;
  height: 40px;
  width: 140px;
  font-size: 100%;
  box-shadow: ${props => props.disabled? '' : '2px 2px 2px #888888'};
  text-overflow:ellipsis;
  overflow: hidden;
  margin-left: 20px;
`;

/**
 * Component for buttons on the model and query application pages.
 * @param {object} props Component props
 * @param {function} props.handleClick The function to be called when the button is clicked
 * @param {string} props.label The text that should be displayed within the button
 * @param {boolean} props.active Indicates whether button should be activated
 */
function ModelButton(props){
  return( 
    <Button disabled={!props.active} onClick={props.handleClick}> {props.label} </Button>
  );
}

export default ModelButton;