import React, { Component } from "react";
import { Marker } from "react-map-gl";
import ReactMapGL from "react-map-gl";
import "mapbox-gl/dist/mapbox-gl.css";
import axios from "axios";
import pin from "./mapbox-marker-icon-20px-gray.png";

const mapboxToken =
  "pk.eyJ1IjoiY21qNzAiLCJhIjoiY2txa2dhN3M0MDM4eDJucDJwZGZlaTF2dSJ9.hS4F34MrElRgSSmGJy_Oiw";

class Map extends Component {
  constructor() {
    super();

    this.state = {
      markers: [],
      viewport: {
        width: "80%",
        height: "100vh",
        latitude: 30.2672,
        longitude: -97.7431,
        zoom: 11,
      },
      loading: false,
      showSide: false,
      clickObj: null
    };
    this.handleViewportChange = this.handleViewportChange.bind(this);
  }

  triggerSidebar(marker) {
      console.log("test")
    this.setState({clickObj: marker, showSide: true})
  }

  componentDidMount() {
    // have this align with the mapping instead of the api call maybe
    this.setState({ loading: true }, () => {
      axios.get("http://127.0.0.1:5000/").then((result) =>
        this.setState({
          loading: false,
          markers: result.data.result,
        })
      );
    });
  }

  handleViewportChange(viewport) {
    this.setState((prevState) => ({
      viewport: { ...prevState.viewport, ...viewport },
    }));
  }

  render() {
    return (
        // make the mapping process asynchronous so some points show up? if thats what works?
      <ReactMapGL
        {...this.state.viewport}
        onViewportChange={(viewport) => this.setState({ viewport })}
        // width="100%"
        // height="100%"
        mapboxApiAccessToken={mapboxToken}
        mapStyle="mapbox://styles/mapbox/streets-v10"
      >
        {/* <Marker
          // offsetTop={-48}
          // offsetLeft={-24}
          latitude={30.2672}
          longitude={-97.743}
          key={1}
        >
          <img src={pin} alt="Pin" />
        </Marker> */}
        {this.state.markers.slice(0,100).map(
          (marker, index) => (
            console.log(marker),
            (
              <Marker
                // offsetTop={-48}
                // offsetLeft={-24}
                latitude={marker.lat}
                longitude={marker.long}
                key={index}
                onClick={(marker) => this.triggerSidebar(marker)}
              >
          <img src={pin} alt="Pin" />
              </Marker>
            )
          )
        )}
      </ReactMapGL>
    );
  }
}

export default Map;
