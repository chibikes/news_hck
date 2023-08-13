import '@fortawesome/fontawesome-free/css/all.min.css';
import './App.css';
import ItemsView from './components/ItemsView';
import { BrowserRouter as Router, Route, Routes, useNavigate} from 'react-router-dom';
import ItemDetail from './components/ItemDetail';

function App() {
  return (
    <Router>
      <Routes>
      <Route path="/" element={<ItemsView />}/>
      <Route path='/item/:itemid' element={<ItemDetail />}/>
      </Routes>
    </Router>
  );
}

export default App;
