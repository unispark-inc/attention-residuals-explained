# Attention Residuals Explained

[![GitHub Pages](https://img.shields.io/badge/demo-live-success)](https://unispark-inc.github.io/attention-residuals-explained)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

An interactive visual explanation of MoonshotAI's **Attention Residuals** paper, which proposes replacing standard fixed residual connections in Transformers with learned, input-dependent attention over depth.

[**📖 View the Interactive Explainer**](https://unispark-inc.github.io/attention-residuals-explained)

![Preview](./assets/og-image.png)

## What is Attention Residuals?

Standard Transformers use fixed residual connections where each layer's output is added to a residual stream with unit weights: `h_l = h_{l-1} + f_l(h_{l-1})`.

This creates three fundamental problems:
1. **No selective access** — all layers receive the same aggregated state
2. **Irreversible information loss** — individual layer contributions cannot be recovered
3. **Output magnitude growth** — deeper layers must produce larger outputs to remain influential

**Attention Residuals** solves this by replacing fixed summation with learned attention:

```
h_l = Σ α_{i→l} · v_i   for i=0 to l-1
```

Each layer computes attention weights over all previous layer outputs using learned pseudo-query vectors, enabling selective, content-aware access to earlier representations.

### Two Variants

1. **Full AttnRes**: Each layer attends over all previous outputs (O(Ld) memory)
2. **Block AttnRes**: Partition layers into blocks, attention over block-level representations (O(Nd) memory) — practical for scale

### Key Results

Block AttnRes achieves:
- **~1.25x compute reduction**
- **+7.5 points** on GPQA-Diamond
- **+3.1 points** on HumanEval
- Matches or exceeds baseline on MMLU and Math benchmarks

## Features

This interactive explainer includes:

- **Scroll-based animations** showing the evolution from standard residuals to attention residuals
- **Interactive diagrams** demonstrating how attention weights are computed
- **Adjustable visualizations** for exploring different numbers of blocks
- **Dark/light mode** toggle
- **Mobile responsive** design
- **Zero dependencies** — pure HTML/CSS/JS using vanilla SVG

## Local Development

```bash
# Clone the repository
git clone https://github.com/unispark-inc/attention-residuals-explained.git
cd attention-residuals-explained

# Open in browser (no build step needed!)
open index.html
# or
python -m http.server 8000  # then visit localhost:8000
```

## Project Structure

```
attention-residuals-explained/
├── index.html              # Main explainer page
├── css/
│   └── style.css           # Styles and animations
├── js/
│   ├── diagrams.js         # SVG diagram rendering
│   └── interactive.js      # User controls & scroll animations
├── assets/
│   └── og-image.png        # Social preview image
├── .github/
│   └── workflows/
│       └── pages.yml       # GitHub Pages deployment
└── README.md
```

## Contributing

Contributions are welcome! Here are some ideas:

- Add more interactive examples
- Improve mobile responsiveness
- Add more detailed mathematical explanations
- Create additional visualizations for the paper's ablation studies
- Add internationalization (i18n) support

To contribute:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## Citation

If you use this explainer in your work or find it helpful, please cite the original paper:

```bibtex
@article{ye2025attention,
  title={Attention Residual: Generalizing Residual to Attention},
  author={Ye, Zhuoyan and Liu, Yilei and Zhang, Zikang and Gu, Yutao and others},
  journal={arXiv preprint arXiv:2501.12245},
  year={2025}
}
```

## Resources

- [ArXiv Paper](https://arxiv.org/abs/2501.12245)
- [Official Implementation](https://github.com/MoonshotAI/Attention-Residual)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- MoonshotAI/Kimi team for the original research
- Inspired by Jay Alammar's [The Illustrated Transformer](http://jalammar.github.io/illustrated-transformer/)

---

Built with ❤️ for the ML community
