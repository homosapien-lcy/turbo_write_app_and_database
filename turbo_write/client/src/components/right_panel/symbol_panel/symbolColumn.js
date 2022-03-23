import React, { Component } from "react";

class SymbolColumn extends React.Component {
  render() {
    return (
      <div key="symbol-column">
        <div style={{ margin: "15px 10px" }}>
          <font color="white">请复制您想添加的符号并粘帖在正文中</font>
        </div>
        <div style={{ margin: "15px 10px" }}>
          <font color="white">希腊字母</font>
          <br />
          <font color="white">
            θ ω ε ρ τ ψ υ ι ο π α σ δ φ γ η ς κ λ ζ χ ξ ω β ν μ
          </font>
        </div>
        <div style={{ margin: "15px 10px" }}>
          <font color="white">数学符号</font>
          <br />
          <font color="white">⊥ ∥ ∠ ⌒ ⊙ ≡ ≌ </font>
          <br />
          <font color="white">∝ ∧ ∨ ～ ∫ ∮ ⊕ ⊙</font>
          <br />
          <font color="white">± ≠ ≤ ≥ ≮ ≯ ≈</font>
          <br />
          <font color="white">∪ ∩ ⊆ ⊂ ⊇ ⊃ ∈</font>
          <br />
          <font color="white">← → ∴ ∵ ∶ ∷</font>
          <br />
          <font color="white">℃ Å ∞ △</font>
        </div>
      </div>
    );
  }
}

export default SymbolColumn;
