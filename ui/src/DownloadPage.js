import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { toast, ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import {
  Container,
  TextField,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper
} from '@mui/material';

function DownloadPage() {
  const [videoUrl, setVideoUrl] = useState('');
  const [items, setItems] = useState([]);

  const downloadAudio = async () => {
    try {
      const response = await axios.post('http://localhost:8000/download', { url: videoUrl });
      toast.success(response.data.message, {
        position: "bottom-left",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
    } catch (error) {
      console.error('Error:', error);
      toast.error('Error starting download', {
        position: "bottom-left",
        autoClose: 5000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
      });
    }
  };

  const getLatestItems = async () => {
    try {
      const response = await axios.get('http://localhost:8000/get_latest');
      setItems(response.data.items.map((item, index) => ({
        name: item,
        last_modified: new Date(response.data.items_last_modified[index]).toLocaleString(),
      })));
    } catch (error) {
      console.error('Error getting latest items:', error);
    }
  };

  useEffect(() => {
    getLatestItems();
    const interval = setInterval(getLatestItems, 5000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Container>
      <TextField
        value={videoUrl}
        onChange={(e) => setVideoUrl(e.target.value)}
        label="YouTube URL"
        fullWidth
        margin="normal"
        onKeyPress={(e) => {
          if (e.key === 'Enter') {
            downloadAudio();
          }
        }}
      />

      <Typography variant="h5" style={{ marginTop: '2rem', textDecoration: 'underline' }}>
        Downloaded
      </Typography>

      <TableContainer component={Paper} style={{ marginTop: '1rem' }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>File Name</TableCell>
              <TableCell>Last Modified</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((item, index) => (
              <TableRow key={index}>
                <TableCell>{item.name}</TableCell>
                <TableCell>{item.last_modified}</TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      <ToastContainer />
    </Container>
  );
}

export default DownloadPage;