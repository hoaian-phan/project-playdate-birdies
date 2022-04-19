// This REACT file is used to update changing states of total participants and their names
// after a successful registration without reloading the page

// Registration with name and number of people
const RegistrationForm = (props) => {
    // useState to keep track of changing states
    const [name, setName] = React.useState([]);
    const [number, setNumber] = React.useState([]);
    const [reminder, setReminder] = React.useState([]);

    // Register by sending AJAX to server and add registration to database
    const register = () => {
        fetch("/register", {
            method: 'POST',
            body: JSON.stringify({'name': name, 'num_people': number, 'reminder': reminder}),
            headers: {
                'Content-Type': 'application/json',
            },
        })
        .then(response => response.json())
        .then(responseJson => {
            if (responseJson.success === true) {
                props.setCount(count => count + responseJson.registration.num_people);
                props.setParticipants(participants => [... participants, responseJson.registration.name]);
                alert("Successfully registered for this playdate");
            } else {
                alert("You've already registered for this playdate.");
            } 
        })
    }
    return (
        <div><br></br>
            <h2 class="text-center fw-bold">Tell us about you</h2><br></br>
            <div class="form-floating mb-3">
                <input
                    class="form-control"
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    id="name"
                ></input><br />
                <label 
                    class="form-label" 
                    htmlFor="name">
                        What is your name?
                </label>
            
            </div>

            <div class="form-floating mb-3">
                <input
                    class="form-control"
                    value={number}
                    onChange={(event) => setNumber(event.target.value)}
                    id="people"
                ></input><br />
                <label 
                    class="form-label" 
                    htmlFor="people">
                        How many people in your party?
                </label>
                
            </div>

            <label htmlFor="reminder">Do you want to receive an email reminder for your playdate?</label><br />
            <div class="form-check">
                <input
                    class="form-check-input"
                    type="radio"
                    value="yes"
                    onChange={(event) => setReminder(event.target.value)}
                    id="yesReminder"
                    checked
                ></input>
                <label 
                    class="form-check-label"
                    htmlFor="yesReminder"> 
                        Yes 
                </label>
            </div>

            <div class="form-check">
                <input
                    class="form-check-input"
                    type="radio"
                    value="no"
                    onChange={(event) => setReminder(event.target.value)}
                    id="noReminder"
                ></input>
                <label 
                    class="form-check-label"
                    htmlFor="noReminder"> 
                        No 
                </label>
            </div>
           
            <div class="mt-3 text-center">
                <button 
                    class="btn btn-primary btn-md"
                    onClick={() => {
                        const confirmBox = window.confirm("Do you want to register for this playdate?")
                        if (confirmBox) {
                            register()
                        }
                    }}>Register</button>
            </div>
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

    // to show different messages when nobody has registered yet
    const showNumber = () => {
        if (count) {
            return (
                <div><br /><br />
                    <p>Total number of participants: {count}</p>
                    <p>Who's coming: Families of {participants.join(", ")}</p>
                </div>
                )
        } else {
            return (
                <p>Nobody has registered for this playdate yet</p>
            )
        }
    }
    
    return (
        <div>
            <RegistrationForm setCount={setCount} setParticipants={setParticipants} />
            {showNumber()}
        </div>
    )

}


// Total page component to render
ReactDOM.render(<RegistrationContainer />, document.getElementById('root'));