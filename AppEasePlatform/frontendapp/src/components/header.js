import React from 'react';
import styled from 'styled-components';
import HeaderButton from './header-button';

// Styling for the header background.
const Banner = styled.div`
  height: 130px;
  width: 100vw;
  display: inline-block;
  background-color: #C4C4C4;
  position: sticky;
  top: 0;
  z-index: 9999;
`;

// Styling for the header title.
const Title = styled.h1`
  margin-top: 6px;
  margin-bottom: 15px;
`;

/**
 * Component for the application header.
 */
function Header(){

  if (window.location.pathname === '/') return null;
  /**
   * A function called when the header title is clicked. Navigates to the home page
   * application.
   */
  function navigate(){
    window.location = ('/home');
  }

  return(
    <Banner>
      <Title onClick={navigate}> AppEase </Title>
      <HeaderButton label="Model" route="model"/>
      <HeaderButton label="Visualize" route="visualize"/>
      <HeaderButton label="Query" route="query"/>
      <HeaderButton label="Monitor" route="monitor"/>
    </Banner>
  );
}

export default Header;
