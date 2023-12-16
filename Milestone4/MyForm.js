import React, { useState, useEffect } from 'react';
import graph from './predicted_graph.png'
import stocks from './stocks.txt'
import { toBeChecked } from '@testing-library/jest-dom/matchers';
import techData from './tech.json'


const MyForm = () => {
    const [selectedOption, setSelectedOption] = useState('');
    const [options, setOptions] = useState([]);
    const [imageUrl, setImageUrl] = useState('');
    const [tech, setTech] = useState({});
    const [stock, setStock] = useState('');
    const [sen, setSen] = useState('');


    useEffect(() => {
        fetch(stocks)
        .then((response) => response.text())
        .then((text) => {
            const lines = text.split('\n');
            setOptions(lines);
        });

        const techVar = async() => {await fetch(`http://localhost:5000/tech/${stock}`)
        .then(response => {
            console.log(tech.beta)
            console.log('use effects')
        })
        .catch(error => console.log(error))}
        console.log('tech data use effects')
        console.log(techData)

    }, [stock, tech]);

  // Handle the form submission
  const handleSubmit = (event) => {
    event.preventDefault(); // Prevents the default form submit action
    alert(`Selected option: ${selectedOption}`); // Example action on form submit
    setStock(selectedOption)
    fetch(`http://localhost:5000/predict/${selectedOption}`)
      .then(response => {
        setImageUrl('predicted_graph')
      })
      .catch(error => console.log(error))

    fetch(`http://localhost:5000/tech/${selectedOption}`)
      .then(response => {
        setTech(response)
        console.log(response.toString())
        console.log('text')
      })
      .catch(error => console.log(error))

    // fetch(`http://localhost:5000/sen/${selectedOption}`)
    //   .then(response => {
    //     setSen(response)
    //     console.log('sentiment')
    //     console.log(response)
    //   })
    //   .catch(error => console.log(error))
    

  };

  // Update state when the select option changes
  const handleSelectChange = (event) => {
    setSelectedOption(event.target.value);
  };

  // Render the form
  
  return (
    <div style={{ backgroundColor: '#120323', padding: '20px', color: 'white' }}>
      <form onSubmit={handleSubmit}>
        <label>
          <h3>Choose a stock:</h3>
          <select value={selectedOption} onChange={handleSelectChange}>
            <option value="">Select...</option>
            {options.map((option, index) => (
              <option key={index} value={option}>{option}</option>
            ))}
          </select>
        </label>
        <br></br>
        <br></br>
        <button type="submit" class='center'>Submit</button>
      </form>

      <br/>
      <table>
        <tr>
            <th>
            {imageUrl&&<img src={graph}/>}
            </th>
            <th>
                <table style={{textAlign: 'right'}}>
                {/* <h3>News Sentiment Score: {sen}</h3> */}
                {Object.entries(techData).map(([key, value]) => (
                    <tr>
                        <th>   </th>
                        <th>        {key}</th>
                        <th>   </th>
                        <th>  {value}</th>
                    </tr>
                ))} 
                </table>
            </th>
        </tr>
      </table>
      
    </div>
  );
};

export default MyForm;
