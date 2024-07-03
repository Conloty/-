import React, { useState } from 'react';
import axios from 'axios';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';

function SearchPage() {
  const [search, setSearch] = useState({ jobTitle: '', company: '', city: '', workFormat: 'remote' });
  const navigate = useNavigate();

  const handleChange = (e) => setSearch({ ...search, [e.target.name]: e.target.value });

  const handleSearch = async (e) => {
    e.preventDefault();
    try {
      const { data } = await axios.post('/api/parse', search);
      navigate('/results', { state: { results: data } });
    } catch (error) {
      console.error("Ошибка при получении данных:", error);
    }
  };

  return (
    <div>
      <h1>Поиск вакансий</h1>
      <form onSubmit={handleSearch}>
        <input type="text" name="jobTitle" placeholder="Название должности" value={search.jobTitle} onChange={handleChange} />
        <input type="text" name="company" placeholder="Компания" value={search.company} onChange={handleChange} />
        <input type="text" name="city" placeholder="Город" value={search.city} onChange={handleChange} />
        <select name="workFormat" value={search.workFormat} onChange={handleChange}>
          <option value="remote">Удалёнка</option>
          <option value="office">Офис</option>
        </select>
        <button type="submit">Поиск</button>
      </form>
    </div>
  );
}

function ResultsPage() {
  const { state } = useLocation();
  const [results, setResults] = useState(state?.results || []);
  const [filters, setFilters] = useState({ jobTitle: '', company: '', city: '', workFormat: '' });

  const handleChange = (e) => setFilters({ ...filters, [e.target.name]: e.target.value });

  const fetchResults = async () => {
    try {
      const { data } = await axios.get('/api/vacancies', { params: filters });
      setResults(data);
    } catch (error) {
      console.error("Ошибка при получении данных:", error);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchResults();
  };

  return (
    <div>
      <h1>Результаты поиска</h1>
      <form onSubmit={handleSearch}>
        <input type="text" name="jobTitle" placeholder="Название должности" value={filters.jobTitle} onChange={handleChange} />
        <input type="text" name="company" placeholder="Компания" value={filters.company} onChange={handleChange} />
        <input type="text" name="city" placeholder="Город" value={filters.city} onChange={handleChange} />
        <select name="workFormat" value={filters.workFormat} onChange={handleChange}>
          <option value="remote">Удалёнка</option>
          <option value="office">Офис</option>
        </select>
        <button type="submit">Применить фильтры</button>
      </form>
      {results.map((result, index) => (
        <div key={index}>
          <h2>{result.Вакансия}</h2>
          <p>{result.Компания}</p>
          <p>{result.Город}</p>
          <p>{result.Формат_работы}</p>
          <a href={result.Ссылка}>Подробнее</a>
        </div>
      ))}
    </div>
  );
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<SearchPage />} />
      <Route path="/results" element={<ResultsPage />} />
    </Routes>
  );
}

export default App;
