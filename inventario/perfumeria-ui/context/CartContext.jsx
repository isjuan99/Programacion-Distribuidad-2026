import { createContext, useContext, useReducer } from "react";

const CartCtx = createContext(null);

function cartReducer(state, action) {
  switch (action.type) {
    case "ADD": {
      const ex = state.find(i => i.id === action.item.id);
      if (ex) return state.map(i =>
        i.id === action.item.id ? { ...i, qty: i.qty + 1 } : i
      );
      return [...state, { ...action.item, qty: 1 }];
    }
    case "REMOVE":  return state.filter(i => i.id !== action.id);
    case "SET_QTY": return state.map(i =>
      i.id === action.id ? { ...i, qty: Math.max(1, action.qty) } : i
    );
    case "CLEAR":   return [];
    default:        return state;
  }
}

export function CartProvider({ children }) {
  const [items, dispatch] = useReducer(cartReducer, []);

  const addItem    = (item)      => dispatch({ type: "ADD",     item });
  const removeItem = (id)        => dispatch({ type: "REMOVE",  id });
  const setQty     = (id, qty)   => dispatch({ type: "SET_QTY", id, qty });
  const clearCart  = ()          => dispatch({ type: "CLEAR" });

  const total    = items.reduce((s, i) => s + i.precio * i.qty, 0);
  const totalQty = items.reduce((s, i) => s + i.qty, 0);

  return (
    <CartCtx.Provider value={{ items, addItem, removeItem, setQty, clearCart, total, totalQty }}>
      {children}
    </CartCtx.Provider>
  );
}

export const useCart = () => useContext(CartCtx);
