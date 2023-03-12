import React from 'react';

interface WasteData {
  previsione_status: Date;
  riempimento: number;
  status: number;
}

interface WasteInfo {
  [key: string]: WasteData;
}

interface Props {
  wasteList: WasteInfo;
}

const WasteListComponent: React.FC<Props> = ({ wasteList }) => {
  if (!wasteList) return (<div className='text-bold'>Loading</div>);

  return (
    <div>
      {Object.keys(wasteList).map((wasteInfoKey, index) => {
      const wasteInfo = wasteList[wasteInfoKey as keyof WasteInfo];
        return (
          <div key={index}>
            <h3>Tipologia di rifiuto: {wasteInfoKey}</h3>
            <div>Stato: {wasteInfo.status}</div>
          </div>
        );
      })}
    </div>
  );
};

export default WasteListComponent;