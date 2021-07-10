import React, { Component } from "react";
import MapGL, { Source, Layer } from "react-map-gl";
// import Geocoder from "react-mapbox-gl-geocoder";
import "mapbox-gl/dist/mapbox-gl.css";
// import 'react-map-gl-geocoder/dist/mapbox-gl-geocoder.css'
// import axios from "axios";
// import grayMarker from "./grayMarker.png";
import propertyMarkers from "./property_markers.json";

const mapboxToken =
  "pk.eyJ1IjoiY21qNzAiLCJhIjoiY2txa2dhN3M0MDM4eDJucDJwZGZlaTF2dSJ9.hS4F34MrElRgSSmGJy_Oiw";

const dataLayer = {
  id: "markers",
  type: "symbol",
  // source: "points", // or maybe just data?
  // "source-layer": "landuse",
  // filter: ["==", "class", "park"],
  layout: {
    "icon-image": "marker-15", // likely wrong
    "icon-allow-overlap": false,
  },
};

// const params = {
//   city: "austin",
// };

class Map extends Component {
  constructor() {
    super();

    this.state = {
      viewport: {
        width: "80%",
        height: "80vh",
        latitude: 30.2672,
        longitude: -97.7431,
        zoom: 11,
      },
      loading: false,
      showSide: false,
      clickObj: null,
    };
    this.handleViewportChange = this.handleViewportChange.bind(this);
  }

  triggerSidebar(marker) {
    console.log("test");
    this.setState({ clickObj: marker, showSide: true });
  }

  // componentDidMount() {
  //   // have this align with the mapping instead of the api call maybe
  //   this.setState({ loading: true }, () => {
  //     axios.get("http://127.0.0.1:5000/").then((result) =>
  //       this.setState({
  //         loading: false,
  //         markers: result.data.result,
  //       })
  //     );
  //   });
  // }

  handleViewportChange(viewport) {
    this.setState((prevState) => ({
      viewport: { ...prevState.viewport, ...viewport },
    }));
  }

  render() {
    return (
      // make the mapping process asynchronous so some points show up? if thats what works?
      <MapGL
        {...this.state.viewport}
        // width="100%"
        // height="100%"
        // latitude={30.2672}
        // longitude={-97.7431}
        // zoom={11}
        mapStyle="mapbox://styles/mapbox/streets-v9"
        onViewportChange={(viewport) => this.setState({ viewport })}
        mapboxApiAccessToken={mapboxToken}
        // interactiveLayerIds={['data']}
        // onHover={onHover}
      >
        {/* <Geocoder
          mapboxApiAccessToken={mapboxToken}
          onSelected={(viewport) => this.setState({ viewport })}
          viewport={this.state.viewport}
          hideOnSelect={true}
          value=""
          queryParams={params}
        /> */}
        <Source type="geojson" data={propertyMarkers}>
          <Layer {...dataLayer} />
          {/* <Feature
            coordinates={markerCoord}
            onHover={this._onHover}
            onEndHover={this._onEndHover}
            onClick={this._onClickMarker}/> */}
          {/* {this.state.markers.slice(0, 100).map(
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
                  <img src={grayMarker} alt="Pin" />
                </Marker>
              )
            )
          )} */}
        </Source>
        {/* {hoverInfo && (
          <div className="tooltip" style={{left: hoverInfo.x, top: hoverInfo.y}}>
            <div>State: {hoverInfo.feature.properties.name}</div>
            <div>Median Household Income: {hoverInfo.feature.properties.value}</div>
            <div>Percentile: {(hoverInfo.feature.properties.percentile / 8) * 100}</div>
          </div>
        )} */}
      </MapGL>
    );
  }
}

export default Map;
