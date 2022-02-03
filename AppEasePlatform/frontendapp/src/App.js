import './App.css';
import { BrowserRouter, Switch, Route, NavLink } from 'react-router-dom';
import Login from './components/login';
import Monitor from './components/monitor';
import React from 'react';
import 'bootstrap/dist/css/bootstrap.min.css';
import Header from './components/header'
import Home from './components/home'
import Model from './components/model'
import Query from './components/query'
import Visualize from './components/visualize'
function App() {

  return (
    <div className = "App" >
      <BrowserRouter>
        <div>
          <div className="content">
          <Header/>
            <Switch>
              <Route exact path="/" component={Login} />
              <Route path="/home" component={Home} />
              <Route path="/model" component={Model} />
              <Route path="/visualize" component={Visualize} />
              <Route path="/monitor" component={Monitor} />
              <Route path="/query" component={Query} />
            </Switch>
          </div>
        </div>
      </BrowserRouter>
    </div>
  );
}

export default App;
