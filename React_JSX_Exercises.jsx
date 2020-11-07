{/*COUNTER BUTTONS EXERCISE*/}
class Counter extends React.Component {
    constructor(props) {
      super(props);
      this.state = {
        count: 0
      };
      // Change code below this line
      this.increment = this.increment.bind(this);
      this.decrement = this.decrement.bind(this);
      this.reset = this.reset.bind(this);
      // Change code above this line
    }
    // Change code below this line
      reset () {
        this.setState({
          count:0
        });
      }
      increment () {
        this.setState(state => ({
          count: state.count + 1
        }));
      }
      decrement () {
        this.setState(state => ({
          count: state.count - 1
        }))
      }
    // Change code above this line
    render() {
      return (
        <div>
          <button className='inc' onClick={this.increment}>Increment!</button>
          <button className='dec' onClick={this.decrement}>Decrement!</button>
          <button className='reset' onClick={this.reset}>Reset</button>
          <h1>Current Count: {this.state.count}</h1>
        </div>
      );
    }
  };

{/*Controlled Input*/}
class ControlledInput extends React.Component {
    constructor (props){
        super (props);
        this.state = {
            input = ''
        };
    }

    handleChange(event){
        this.setState ({
            input: event.target.value
        });
    }

    render () {
        return (
            <div>
                <input value={this.state.input} onChange = {this.handleChange.bind(this)}></input>
                <h4>Controlled Input:</h4>
                <p>{this.state.input}</p>
            </div>
        );
    }
};

{/*Controlled Form*/}
class MyForm extends React.Component {
    constructor (props){
        super(props);
        this.state = {
            input: '',
            submit: ''
        };
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }
    handleChange(event) {
        this.setState ({
            input: event.target.value
        });
    }
    handleSubmit(event) {
        event.preventDefault()
        this.state({
            submit: this.state.input
        }); 
    }
    render () {
        return (
            <div>
                <form onSubmit={this.handleSubmit}>
                    <input 
                    value = {this.state.input}
                    onChange = {this.handleChange}/>
                    <button type='submit'>Submit!</button>
                </form>
                <h1>{this.state.submit}</h1>
            </div>
        );
    }
}

{/*Pass State as props to child components*/}

class MyApp extends React.Component {
  constructor (props){
    super(props);
    this.state {
      name: 'CamperBot'
    }
  }
  render () {
    return (
      <div> 
        <Navbar name={this.state.name}/>
      </div>
    );
  }
};

class Navbar extends React.Component{
  constructor (props){
    super (props);
  }
  render () {
    return (
      <div>
        <h1>Hello, my name is {this.props.name} </h1>
      </div>
    );
  }
}

{/*Pass a Callback as Props*/}
class MyApp extends React.components {
  constructor (props){
    super(props);
    this.state = {
      inputValue: ''
    }
    this.handleChange = this.handleChange.bind(this);
  }
  handleChange(event){
    this.setState ({
      inputValue: event.target.value
    });
  }
  render () {
    return (
      <div>
        <GetInput input={this.state.inputValue} handleChange = {this.handleChange}/>
        <RenderInput input={this.state.inputValue}/>
      </div>
    );
  }
}

class GetInput extends React.Component{
  constructor (props){
    super(props);
  }
  render(){
    return (
      <div>
        <h3> Get Input:</h3>
        <input
        value={this.props.input}
        onChange={this.props.handleChange}/>
      </div>
    );
  }
};

class RenderInput extends React.Component {
  constructor (props){
    super(props);
  }
  render (){
    return (
      <div>
        <h3>Input Render:</h3>
        <p>{this.props.input}</p>
      </div>
    );
  }
}

{/*Use the Lifecycle Method componentDidMount*/}
class MyComponent extends React.Component {
  constructor (props){
    super(props);
    this.state = {
      activeUsers: null
    };
  }
//Mock API Call
  componentDidMount(){
    setTimeout(() => {
      this.setState({
        activeUsers: 1273
      });
    }, 2500);
  }
  render() {
    return (
      <div>
        <h1>Active Users: {this.state.activeUsers}</h1>
      </div>
    );
  }
};

{/*Add Event Listeners*/}
class MyComponent extends React.Component {
  constructor (props){
    super(props);
    this.state = {
      message: ''
    };
    this.handleEnter = this.handleEnter.bind(this);
    this.handleKeyPress = this.handleKeyPress.bind(this);
  }
  componentDidMount(){
    document.addEventListener ("keydown", this.handleKeyPress);
  }
  componentWillUnmount(){
    document.removeEventListener("keydown", this.handleKeyPress);
  }
  handleEnter (){
    this.setState((state) => ({
      message: state.message + 'You pressed the enter key!'
    }));
  }
  handleKeyPress(event){
    if (event.keyCode === 13) {
      this.handleEnter();
    }
  }
  render (){
    return (
      <div>
        <h1>{this.state.message}</h1>
      </div>
    );
  }
};

{/*Optimize Re-renders with shouldComponentUpdate*/}
class OnlyEvens extends React.Component {
  constructor (props){
    super(props);
  }
  shouldComponentUpdate(nextProps, nextState) {
    console.log('Should I update?');
    if (nextProps.value % 2 == 0){
      return true;
    }
    return false;
  }
  componentDidUpdate(){
    console.log('Component re-rendered.');
  }
  render(){
    return <h1>{this.props.value}</h1>;
  }
}
class Controller extends React.Component {
  constructor (props){
    super(props);
    this.state = {
      value:0
    };
    this.addValue = this.addValue.bind(this);
  }
  addValue() {
    this.setState(state=> ({
      value: state.value + 1
    }));
  }
  render (){
    return (
      <div>
        <button onClick={this.addValue}>Add</button>
        <OnlyEvens value={this.state.value} />
      </div>
    );
  }
}

{/*Add Inline Styles in React*/}
const styles = {
  color: 'purple',
  fontSize: 40,
  border: "2px solid purple"
};
class Colorful extends React.Component {
  render (){
    return (
      <div style={styles}> Style Me</div>
    );
  }
}

{/*Use Advanced JavaScript in React Render Method*/}
const inputStyle = {
  width: 235,
  margin: 5,
};

class MagicEightBall extends React.Component {
  constructor(props){
    super (props);
    this.state = {
      userInput: '',
      randomIndex: '',
    };
    this.ask = this.ask.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }
  ask() {
    if (this.state.userInput){
      this.setState({
        randomIndex:Math.floor(Math.random() * 20), 
        userInput: ''
      });
    }
  }
  handleChange(){
    this.setState({
      userInput: event.target.value
    });
  }
  render (){
    const possibleAnswers = [
      'It is certain',
      'It is decidedly so',
      'Without a doubt',
      'Yes, definitely',
      'You may rely on it',
      'As I see it, yes',
      'Outlook good',
      'Yes',
      'Signs point to yes',
      'Reply hazy try again',
      'Ask again later',
      'Better not tell you now',
      'Cannot predict now',
      'Concentrate and ask again',
      "Don't count on it",
      'My reply is no',
      'My sources say no',
      'Most likely',
      'Outlook not so good',
      'Very doubtful'
    ];
    const answer = possibleAnswers[this.state.randomIndex];
    return (
      <div>
        <input type='text' 
        value={this.state.userInput}
        onChange={this.handleChange}
        style={inputStyle}
        />
        <br />
        <button onClick={this.ask}>Ask the Magic Eight Ball!</button>
        <br />
        <h3> Answer: </h3>
        <p>
          {answer}
        </p>
      </div>
    );
  }
}


{/*Render Conditionally from Props*/}
class Results extends React.Component {
  constructor (props){
    super(props);
  }
  render (){
  return <h1>{this.props.fiftyFifty ? "You Win!" : "You Lose!" }</h1>
  }
}

class GameOfChance extends React.Components {
  constructor (props){
    super(props);
    this.state = {
      counter: 1
    };
    this.handleClick = this.handleClick.bind(this);
  }
  handleClick (){
    this.setState({
      counter: this.state.counter + 1
    });
  }
  render () {
    const expression = Math.random() >= 0.5 ? true : false;
    return (
      <div> 
        <button onClick={this.handleClick}> Play Again</button>
        <Results fiftyFifty = {expression} />
        <p>{'turn: ' + this.state.counter}</p>
      </div>
    );
  }
}

{/*Change Inline CSS conditionally Based on Component State*/}
class GateKeeper extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      input: ''
    };
    this.handleChange = this.handleChange.bind(this);
  }
  handleChange (event) {
    this.setState ({input: event.target.value})
  }
  render () {
    let inputStyle = {
      border: '1px solid black'
    };
    if (this.state.input.length > 15 ){
      inputStyle.border = '3px solid red'
    }
    return (
      <div>
        <h3> Don't Type Too Much:</h3>
        <input
        type='text'
        style={inputStyle}
        value={this.state.input}
        onChange={this.handleChange}
        />
      </div>
    );
  }
};

{/*Use Array.map() to Dynamically Render Elements*/}
const textAreaStyles = {
  width: 235,
  margin: 5
};
class MyToDoList extends React.Component {
  constructor (props){
    super(props);
    this.state = {
      userInput = '',
      toDoList: [],
    }
    this.handleSubmit = this.handleSubmit.bind(this);
    this.handleChange = this.handleChange.bind(this);
  }
  handleSubmit() {
    const itemsArray = this.state.userInput.split(',');
    this.setState({
      toDoList: itemsArray
    });
  }
  handleChange(e) {
    this.setState({
      userInput: e.target.value
    });
  }
  render () {
  const items = this.state.toDoList.map(i => <li>{i}</li>);
    return (
      <div>
        <textarea 
        onChange = {this.handleChange}
        value= {this.state.userInput}
        style= {textAreaStyles}
        placeholder='Separate Items With Commas'
        />
        <br />
        <button onClick = {this.handleSubmit}> Create List</button>
        <h1> My "TO DO" List:</h1>
        <ul>{items}</ul>
      </div>
    );
  }
}

{/*Give Sibling Elements a Unique Key Attribute*/}
const frontEndFrameworks = [
  'React',
  'Angular',
  'Ember',
  'Knockout',
  'Backbone',
  'Vue'
];

function Frameworks(){
 const renderFrameworks = frontEndFrameworks.map(i=> <li key={i+1}>{i}</li>);
 return (
   <div>
     <h1> Popular Front End JavaScript Frameworks</h1>
     <ul>
       {renderFrameworks}
     </ul>
   </div>
 ); 
}

{/*Use array.filter() to dynamically filter an array*/}
class MyComponent extends React.Component {
  constructor(props){
    super(props);
    this.state = {
      users: [
        {
          username: 'Jeff',
          online: true
        },
        {
          username: 'Alan',
          online: false
        },
        {
          username: 'Mary',
          online: true
        },
        {
          username: 'Jim',
          online: false
        },
        {
          username: 'Sara',
          online: true
        },
        {
          username: 'Laura',
          online: true
        }        
      ]
    };
  }
  render () {
    const usersOnline = this.state.users.filter(i => i.online == true);
    const renderOnline = usersOnline.map((i) => <li key={i.username+1}>{i.username}</li>);
    return (
      <div>
        <h1>Current Online Users:</h1>
        <ul>{renderOnline}</ul>
      </div>
    );
  }
}

{/*Render React on the Server with 'renderToString'*/}
class App extends React.Component {
  constructor (Props) {
    super(props);
  }
  render () {
    return <div/>
  }
};

ReactDOMServer.renderToString(<App />);
