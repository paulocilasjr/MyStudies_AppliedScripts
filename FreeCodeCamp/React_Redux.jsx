//Redux:
const ADD = 'ADD';
const addMessage = (message) => {
    return {
        type: ADD,
        message
    }
};
const messageReducer = (state = [], action) => {
    switch (action.type) {
        case ADD:
            return [...state, action.massage];
        default:
            return state;
    }
};
const store = Redux.createStore(messageReducer);

//React:
class DisplayMessages extends React.Component {
    constructor (props){
        super(props);
        this.state = {
            input: '',
            messages: []
        }
        this.handleChange = this.handleChange.bind(this);
        this.submitMessage = this.submitMessage.bind(this);
    }
    handleChange(event) {
        this.setState({
            input: event.target.value
        });
    }
    submitMessage() {
        this.setState((state) => {
            const currentMessage = state.input;
            return {
                input: '',
                message: state.messages.concat(currentMessage)
            };
        });
    }
    render () {
        return (
            <div>
                <h2>Type in a new Message:</h2>
                <input value={this.state.input} onChange={handleChange}/><br />
                <button onClick={this.submitMessage}>Submit</button>
                <ul>
                    {this.state.messages.map ( (message, idx) => {
                        return (
                        <li key={idx}>{message}</li>
                        )
                    })
                    }
                </ul>
            </div>
        );
    }
};
const Provider = ReactRedux.Provider; 
class AppWrapper extends React.Component {
    render () {
        return (
            <Provider store={store}>
                <DisplayMessages />    
            </Provider>
        );
    }
};

{/*Connect Redux to React*/}
const addMessage = (message) => {
    return {
        type: 'ADD',
        message: message
    }
};
const mapStateToProps = (state) => {
    return {
        message:state
    }
};
const mapDispatchToProps = (dispatch) => {
    return {
        submitNewMessage: (message) => {
            dispatch(addMessage(message));
        }
    }
};
class Presentational extends React.Component {
    constructor (props) {
        super(props);
    }
    render () {
        return <h3>This is a Presentational Component</h3>
    }
};
const connect = ReactRedux.connect;
const ConnectedComponent = connect(mapStateToProps, mapDispatchToProps)(Presentational)

{/*Connect Redux to the Messages App*/}
//Redux
const ADD = 'ADD';
const addMessage = (message) => {
    return {
        type: ADD,
        message: message
    }
};
const messageReducer = (state = [], action) => {
    switch (action.type) {
        case ADD:
            return [...state, action.message];
        default:
            return state;
    }
};
const store = Redux.createStore(messageReducer);
//React
class Presentational extends React.Component {
    constructor(props){
        super(props);
        this.state = {
            input: '',
            messages: []
        }
        this.handleChange = this.handleChange.bind(this);
        this.submitMessage = this.submitMessage.bind(this);
    }
    handleChange(event){
        this.setState({
            input: event.target.value
        });
    }
    submitMessage(){
        this.setState((state)=>{
            const currentMessage = state.input;
            return {
                input: '',
                messages: state.messages.concat(currentMessage)
            };
        });
    }
    render (){
        return (
            <div>
                <h2>Type in a new Message:</h2>
                <input value={this.state.input} onChange={this.handleChange}/><br />
                <button onClick={this.submitMessage}>Submit</button>
                <ul>
                    {this.state.messages.map( (message, idx) => {
                        return (
                            <li key={idx}>{message}</li>
                            )
                        })
                    }
                </ul>
            </div>
        );
    }
};
//React-Redux
const mapStateToProps = (state) => {
    return {messages:state}
};
const mapDispatchToProps = (dispatch) => {
    return {
        submitNewMessage: (newMessage) => {
            dispatch(addMessage(newMessage))
        }
    }
};
const Provider = ReactRedux.Provider;
const connect = ReactRedux.connect;
const Container = connect(mapStateToProps, mapDispatchToProps)(Presentational)

class AppWrapper extends React.Component {
    constructor (props){
        super(props);
    }
    render () {
        return (
            <Provider store={store}>
                <Container />
            </Provider>
        )
    }
};

{/*Extract Local State into Redux*/}
// Redux:
const ADD = 'ADD';

const addMessage = (message) => {
  return {
    type: ADD,
    message: message
  }
};

const messageReducer = (state = [], action) => {
  switch (action.type) {
    case ADD:
      return [
        ...state,
        action.message
      ];
    default:
      return state;
  }
};

const store = Redux.createStore(messageReducer);

// React:
const Provider = ReactRedux.Provider;
const connect = ReactRedux.connect;

// Change code below this line
class Presentational extends React.Component {
  constructor(props) {
    super(props);
    
    // Remove property 'messages' from Presentational's local state
    this.state = {
      input: ''
    }
    this.handleChange = this.handleChange.bind(this);
    this.submitMessage = this.submitMessage.bind(this);
  }
  handleChange(event) {
    this.setState({
      input: event.target.value
    });
  }
  submitMessage() {
  
    // Call 'submitNewMessage', which has been mapped to Presentational's props, with a new message;
    // meanwhile, remove the 'messages' property from the object returned by this.setState().
    this.props.submitNewMessage(this.state.input);
    this.setState({
      input: ''
    });
  }
  render() {
    return (
      <div>
        <h2>Type in a new Message:</h2>
        <input
          value={this.state.input}
          onChange={this.handleChange}/><br/>
        <button onClick={this.submitMessage}>Submit</button>
        <ul>
           {/* The messages state is mapped to Presentational's props; therefore, when rendering,
               you should access the messages state through props, instead of Presentational's
               local state. */}
          {this.props.messages.map( (message, idx) => {
              return (
                 <li key={idx}>{message}</li>
              )
            })
          }
        </ul>
      </div>
    );
  }
};
// Change code above this line

const mapStateToProps = (state) => {
  return {messages: state}
};

const mapDispatchToProps = (dispatch) => {
  return {
    submitNewMessage: (message) => {
      dispatch(addMessage(message))
    }
  }
};

const Container = connect(mapStateToProps, mapDispatchToProps)(Presentational);

class AppWrapper extends React.Component {
  render() {
    return (
      <Provider store={store}>
        <Container/>
      </Provider>
    );
  }
};

{/*Glimpse of what the syntax looks like if you are working with npm and a file system on your own machine*/}
import React from 'react'
import ReactDOM from 'react-dom'
import { Provider, connect } from 'react-redux'
import { createStore, combineReducers, applyMiddleware } from 'redux'
import thunk from 'redux-thunk'

import rootReducer from './redux/reducers'
import App from './components/App'

const store = createStore(
  rootReducer,
  applyMiddleware(thunk)
);

ReactDOM.render(
  <Provider store={store}>
    <App/>
  </Provider>,
  document.getElementById('root')
);

