{/*Create a redux Store*/}
const reducer = (state = 5) => {
    return state;
}

const store = Redux.createStore(reducer);

{/*Get State from the redux store*/}
{const store = Redux.createStore(
    (state = 5) => state
);
const currentState = store.getState()
}

{/*Define a Redux Action and Define an Action Creator*/}
let action = {
    type: 'LOGIN'
}
function actionCreator() {
    return action;
}

{/*Dispatch an Action Event*/}
const store = Redux.createStore(
    (state = {login: false}) => state
);
const loginAction = () => {
    return {
        type: 'LOGIN'
    }
};
store.dispatch(loginAction());

{/*Handle an Action in the store*/}
const defaultState = {
    login: false
};
const reducer = (state = defaultState, action) => {
    if (action.type === 'LOGIN'){
        return {
            login: true
        };
    }else{
        return state;
    }
};
const store = Redux.createStore(reducer);
const loginAction = () => {
    return {
        type: 'LOGIN'
    }
};

{/*Switch Statement to Handle Multiple Actions*/}
const defaultState = {
    authenticated: false
};
const authReducer = (state = defaultState, action) => {
    switch (action.type) {
        case "LOGIN":
            return {
                authenticated: true
            };
        case "LOGOUT":
            return {
                authenticated: false
            };
        default:
            return defaultState;
    }
};
const store = Redux.createStore(authReducer);
const loginUser = () => {
    return {
        type: 'LOGIN'
    }
};
const logoutUser = () => {
    return {
        type: 'LOGOUT'
    }
}

{/*Register a Store Listener*/}
const ADD = 'ADD';
const reducer = (state = 0, action) => {
    switch(action.type) {
        case ADD:
            return state + 1;
        default:
            return state;
    }
};
const store = Redux.createStore(reducer);
let count = 0;

store.subscribe(function (){
    store += 1;
});


store.dispatch({type: ADD});
console.log(count);
store.dispatch({type: ADD});
console.log(count);
store.dispatch({type: ADD});
console.log(count);

{/*Combine multiple reducers*/}
const INCREMENT = 'INCREMENT';
const DECREMENT = 'DECREMENT';
const counterReducer = (state=0, action)=> {
    switch(action.type){
        case INCREMENT:
            return state + 1;
        case DECREMENT:
            return state - 1;
        default:
            return state;
    }
};
const LOGIN = 'LOGIN';
const LOGOUT = 'LOGOUT';
const authReducer = (state = {authenticated:false}, action) => {
    switch(action.type){
        case LOGIN:
            return {
                authenticated: true
            }
        case LOGOUT:
            return {
                authenticated: false
            }
        default:
            return state;
    }
};
const rootReducer = Redux.combineReducers({
    auth: authReducer,
    count: counterReducer
});
const store = Redux.createStore(rootReducer);

{/*Send action Data to the store*/}
const ADD_NOTE = 'ADD_NOTE';
const notesReducer = (state = 'Initial State', action) => {
    switch(action.type) {
        case (ADD_NOTE):
            return action.text;
        default:
            return state;
    }
};
const addNoteText = (note) => {
    return {
        type: ADD_NOTE,
        text: note
    }
};
const store = Redux.createStore(notesReducer);
console.log(store.getState());
store.dispatch(addNoteText('Hello!'));
console.log(store.getState());

{/*Use Middleware to Handle Asynchronous actions*/}

const REQUESTING_DATA = 'REQUESTING_DATA';
const RECEIVED_DATA = 'RECEIVED_DATA';
const requestingData = () => {return {type: REQUESTING_DATA}}
const receivedData = (data) => {return {type:RECEIVED_DATA, users: data.users}}
const handleAsync = () => {
    return function(dispatch) {
        dispatch(requestingData())
        setTimeout (function () {
            let data = {
                users: ['Jeff', 'William', 'Alice']
            }
        dispatch(receivedData(data));
        }, 2500);
    }
};
const defaultState = {
    fetching: false,
    users: []
};
const asyncDataReducer = (state=defaultState, action) => {
    switch(action.type) {
        case REQUESTING_DATA:
            return {
                fetching: true,
                users: []
            }
        case RECEIVED_DATA:
            return {
                fetching: false,
                users: action.users
            }
        default:
            return state;
    }
};
const store = Redux.createStore (asyncDataReducer, Redux.applyMiddleware(ReduxThunk.default)
);

{/*Write a counter with Redux*/}
const INCREMENT = 'INCREMENT';
const DECREMENT = 'DECREMENT'

const counterReducer = (state = 0, action) => {
    switch (action.type) {
        case INCREMENT:
            return state+1;
        case DECREMENT: 
            return state-1;
        default: 
            return state;
        }
}
const incAction = () => {
    return {
        type: INCREMENT
    };
};
const decAction = () => {
    return {
        type: DECREMENT
    };
};
const store = Redux.createStore(counterReducer);

{/*Never mutate state and Add Item*/}
const ADD_TO_DO = 'ADD_TO_DO';
const todos = [
    'Go to the store',
    'Clean the house',
    'Cook diner', 
    'Learn to code',
];
const immutableReducer = (state = todos, action) => {
    switch (action.type) {
        case ADD_TO_DO:
            return [...state, action.todo];
        default: 
            return state;
    }
};

const addToDo = (todo) => {
    return {
        type: ADD_TO_DO,
        todo
    }
}
const store = Redux.createStore(immutableReducer);

{/*Remove an Item from an array*/}
const immutableReducer = (state = [0,1,2,3,4,5], action) => {
    switch (action.type) {
        case 'REMOVE_ITEM':
            return [...state.slice(0, action.index),...state.slice(action.index+1, state.length)];
    }
};
const removeItem = index => {
    return {
        type: "REMOVE_ITEM",
        index
    };
};
const store = Redux.createStore(immutableReducer);

{/*Copy an object with Object.assign*/}
const defaultState = {
    user: 'CamperBot',
    status: 'offline',
    friends: '732,982',
    community: 'freeCodeCamp'
};
const immutableReducer = (state=defaultState, action) => {
    switch(action.type) {
        case 'ONLINE':
            return Object.assign({}, state, {status:"online"});
        default: 
            return state;
    }
};
const wakeUp = () => {
    return {
        type: 'ONLINE'
    }
};
const store = Redux.createStore(immutableReducer);