import Header from './Header.jsx'
import Footer from './Footer.jsx'
import Food from './Food.jsx'

function App() {
  return(
    <>
      <Header></Header> {/*the app menu runs the header function */}
      <Food></Food>
      <Footer></Footer>
      <Text display = "My name is anuj"></Text>
    </>
  );
}

function Text({display}) {   {/* This uses a prop parameter*/}
  return (
    <p>{display}</p>
  );
}
export default App

