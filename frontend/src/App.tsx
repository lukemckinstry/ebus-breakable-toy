import React from 'react';
import Main from "./components/Main";
import { store, persistor } from "./redux/store";
import { PersistGate } from "redux-persist/integration/react";
import { Provider } from 'react-redux';
import { setupInterceptors } from "./redux/api";
import './App.scss';

setupInterceptors(store);

function App() {
  return (
    <Provider store={store}>
      <PersistGate persistor={persistor} loading={null}>
        <div className="App">
          <Main />
        </div>
      </PersistGate>
    </Provider>
  );
}

export default App;
