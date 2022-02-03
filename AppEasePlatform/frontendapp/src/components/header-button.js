import React from 'react';
import styled from 'styled-components';

// Styling for buttons in the header.
const Button = styled.button`
  background-color: #590083;
  color: white;
  border-radius: 12px;
  border: black;
  height: 40px;
  width: 100px;
  font-size: 100%;
  box-shadow: 2px 2px 2px #888888;
  margin-left: 1vw;
  margin-right: 1vw;
  text-overflow:ellipsis;
  overflow: hidden;
  margin-top: 0;
`;

/**
 * Component for buttons in the application header.
 * @param {object} props Component props
 * @param {string} props.route The route to navigate to when the button is clicked
 * @param {string} props.label The text that should be displayed within the button
 */
function HeaderButton(props){

  /**
   * A function called when the button is clicked. Navigates to the url specified
   * by props.route.
   */
  function navigate(){
    window.location = "/" + props.route;
  }

  return(
    <Button onClick={navigate}> {props.label} </Button>
  );
}

export default HeaderButton;
