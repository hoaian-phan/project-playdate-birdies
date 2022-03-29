//console.log("event_id =", event.event_id);

// Registration with name and number of people
const RegistrationForm = (props) => {
    // useState to keep track of changing states
    const [name, setName] = React.useState([]);
    const [number, setNumber] = React.useState([]);

    // Register by sending AJAX to server and add registration to database
    const register = () => {
        alert('trying to register');
        fetch("/register_name", {
            method: 'POST',
            body: JSON.stringify({'name': name, 'num_people': number}),
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(responseJson => {
            props.setCount(count => count + responseJson.registration.num_people);
            props.setParticipants(participants => [... participants, responseJson.registration.name]);
            alert(`Registered for this event ${responseJson.registration.event_title}`);
        })
        
    }
    return (
        <div>
            <h2>Who's coming</h2>
            <label htmlFor="name">Your Name</label>
            <input
                value={name}
                onChange={(event) => setName(event.target.value)}
                id="name"
            ></input><br />
            <label htmlFor="people">How many people in your party?</label>
            <input
                value={number}
                onChange={(event) => setNumber(event.target.value)}
                id="people"
            ></input><br />
            <button onClick={register}>Register</button>
        </div>
    );
}


// Registration form component
const RegistrationContainer = () => {
    // useState to keep track of total count and who's coming
    const [count, setCount] = React.useState(0);
    const [participants, setParticipants] = React.useState([]);
    
    // useEffect to update changes
    React.useEffect(() => {
        fetch("/participants.json")
            .then((reply) => reply.json())
            .then ((data) => {
                setCount(data.counts);
                setParticipants(data.participants);
            })
    }, [])

    const totalNum = count;
    const registeredPartipants = [];

    for (const participant of participants) {
        registeredPartipants.push(participant);
        
    }
    console.log(`how many ${totalNum}`)
    console.log(`who's coming ${registeredPartipants}`);

    return (
        <div>
            <RegistrationForm setCount={setCount} setParticipants={setParticipants} />
            <p>Total number of participants: {totalNum} </p>
            <p>Who's coming: Families of {registeredPartipants.join(", ")}</p>
        </div>
    )

}


// Total page component to render
ReactDOM.render(<RegistrationContainer />, document.getElementById('root'));