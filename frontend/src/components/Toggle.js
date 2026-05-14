import React from 'react';

const Toggle = ({ value, onChange }) => (
  <label className="toggle">
    <input type="checkbox" checked={value} onChange={onChange} />
    <div className="toggle-slider" />
  </label>
);

export default Toggle;
