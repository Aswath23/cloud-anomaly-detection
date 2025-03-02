import React, { useState } from "react";
import Upload from "./Upload";
import Results from "./Results";

function App() {
  const [results, setResults] = useState(null);

  return (
    <div>
      <h1>Cloud Anomaly Detection</h1>
      <Upload setResults={setResults} />
      {results && <Results results={results} />}
    </div>
  );
}

export default App;
