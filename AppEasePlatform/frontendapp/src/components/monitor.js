import React, { Component } from 'react';
import { Redirect } from "react-router-dom";
import { getToken, getUser } from '../utils/common';
import { TimeSeries, Index } from "pondjs";
import {
  Charts,
  ChartContainer,
  ChartRow,
  YAxis,
  LineChart,
  Resizable
} from "react-timeseries-charts";
import CanvasJSReact from '../canvasjs.react';
//var CanvasJSReact = require('./canvasjs.react');
var CanvasJS = CanvasJSReact.CanvasJS;
var CanvasJSChart = CanvasJSReact.CanvasJSChart;

// const user_data = require('../data/user_info.json');
// const health_data = require('../data/health_data.json');
const backendAddress = "192.168.0.154"


class Monitor extends Component {
    state = {
        user_data: {},
        health_data: {},
        name: ''
    }
    componentDidMount() {
        const token = getToken();
        const name = getUser();

        fetch(`http://${backendAddress}:8000/api/healthStatic/${token}/`)
          .then(res => res.json())
          .then(
            (result) => {
              this.setState({
                name: name,
                user_data: result
              });
            },
            // Note: it's important to handle errors here
            // instead of a catch() block so that we don't swallow
            // exceptions from actual bugs in components.
            (error) => {
                console.log(error);
            }
        )
        fetch(`http://${backendAddress}:8000/api/healthDynamic/${token}/`)
          .then(res => res.json())
          .then(
            (result) => {
              this.setState({
                health_data: result
              });
            },
            // Note: it's important to handle errors here
            // instead of a catch() block so that we don't swallow
            // exceptions from actual bugs in components.
            (error) => {
                console.log(error);
            }
        )
      }

    render () {
        if (this.state.user_data.length > 0 && this.state.health_data.length > 0) {
            const user_data = this.state.user_data[0];
            const health_data = this.state.health_data;

            const options = {
                        theme: "light2",
                        animationEnabled: true,
                        title:{
                            text: "Health Data"
                        },
                        subtitles: [{
                            text: ""
                        }],
                        axisX: {
                            title: "Time"
                        },
                        axisY: {
                            title: "Distance (m)",
                            titleFontColor: "#6D78AD",
                            lineColor: "#6D78AD",
                            labelFontColor: "#6D78AD",
                            tickColor: "#6D78AD"
                        },
                        axisY2: {
                            title: "Heart Rate (bpm)",
                            titleFontColor: "#51CDA0",
                            lineColor: "#51CDA0",
                            labelFontColor: "#51CDA0",
                            tickColor: "#51CDA0"
                        },
                        toolTip: {
                            shared: true
                        },
                        legend: {
                            cursor: "pointer",
                            itemclick: this.toggleDataSeries
                        },
                        data: [{
                            type: "line",
                            name: "Distance Traveled",
                            showInLegend: true,
                            xValueFormatString: "DDDD MMM YYYY HH:mm:ss k",
                            yValueFormatString: "###",
                            dataPoints: [
                            ]
                        },
                        {
                            type: "line",
                            name: "Heart Rate",
                            axisYType: "secondary",
                            showInLegend: true,
                            xValueFormatString: "DDDD MMM YYYY HH:mm:ss k",
                            yValueFormatString: "###",
                            dataPoints: [
                            ]
                        }]
                    }
            for (var i = 0; i < health_data.length; i++) {
                let time = new Date(health_data[i].timestamp);
                // time = parseInt(time.getTime());
                let step = parseInt(health_data[i].distancecovered);
                let heart = parseInt(health_data[i].heartrate);

                options.data[0].dataPoints.push({x: time, y: step})
                options.data[1].dataPoints.push({x: time, y: heart})
            }
            return (
                <div className='monitor'>
                    <h3>Monitor</h3>
                    <div>
                        <p><b> Name:</b> {this.state.name} <b>Age:</b> {user_data.age} <b>Sex:</b> {user_data.sex} <b>Blood Type:</b> {user_data.bloodtype}</p>
                    </div>
                    <div>
                        <CanvasJSChart options = {options}
                            onRef={ref => this.chart = ref}/>
                    </div>

                </div>
            );
        }
        else {
            return (
                <div>
                    Loading .....
                </div>
            )
        }
    }
}

export default Monitor;
