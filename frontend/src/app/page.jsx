import Image from "next/image";
import Link from "next/link";
import { LandingNav, Benefits } from "./landing-interactions";

function MissingAsset({ children }) {
  return (
    <div className="missing-asset">
      <span>AWAITING USER ASSET</span>
      <p>{children}</p>
    </div>
  );
}

const comparisons = [
  ["Input costs", "Fertilizers and pesticides can be expensive, and it’s difficult to judge what is necessary.", "Repeat last season’s purchases or rely on generic shelf labels and sales advice.", "Compare possible inputs against soil needs, existing compost/cover crops, plot size, and budget, with estimated costs when pricing data is available."],
  ["Soil complexity", "Soil pH, N-P-K, and crop history are hard to turn into clear actions.", "Leave lab reports unread or interpret them manually across notes and spreadsheets.", "Turn entered soil and growing history into understandable, source-linked nutrient and rotation recommendations, with assumptions visible."],
  ["Weather and pests", "Rainfall changes, planting windows, and recurring pests disrupt a season.", "React after weather shifts or pest damage, often without a coordinated plan.", "Bring available local weather context and research-supported rotation/prevention considerations into one seasonal plan."]
];
const features = [
  ["Field Intelligence", "Understand your soil, crop history, and plot-specific growing conditions.", "Field detail with room for a soil preview.", ["Soil pH — Not provided", "Organic matter — Not provided", "Previous crop — Not provided"]],
  ["Monitoring & Observations", "Keep track of important changes and build a clearer record of each growing season.", "Growing-season observations in an agricultural field.", ["Observations — No records", "Last entry — Unavailable", "Sensors — Not supported"]],
  ["Weather Tracking", "Use local forecasts and relevant growing risks to plan work around changing conditions.", "Weather over a growing field.", ["Forecast — Unavailable", "Source — Not connected", "Last updated — Unavailable"]]
];
export default function Home() {
  return <><a className="skip-link" href="#main">Skip to content</a><main id="main">
    <section className="hero" aria-labelledby="hero-title">
      <Image className="hero-art" src="/assets/images/golden_harvest_tractor_at_sunset.png" alt="" fill sizes="100vw" priority />
      <LandingNav />
      <div className="hero-copy"><h1 id="hero-title">Plantly</h1><h2>Stop Guessing Your Soil.<br />Grow Smarter, Spend Less.</h2><p>Custom, research-backed crop plans and input cost tracking tailored to your exact soil and weather.</p><button className="trial-pill" disabled aria-describedby="trial-note">Try Plantly Free for 7 Days <span aria-hidden="true">↗</span></button><small id="trial-note">In development · Trial not available. Terms are not yet approved.</small></div>
      <div className="hero-scene" aria-hidden="true" />
      <div className="hero-metrics"><div><strong>$36B</strong><span>TAM estimate*</span></div><div><strong>$9.6B</strong><span>SAM proxy*</span></div><div><strong>20%</strong><span>Cost reduction target*</span></div><p>*Historical market proxies; 20% is an unverified savings target.</p></div>
    </section>
    <section id="mission" className="section wrap" aria-labelledby="mission-title"><p className="eyebrow">Our Mission</p><div className="mission-intro"><h2 id="mission-title">Good growing decisions shouldn’t be reserved for big farms.</h2><div><p>Whether you’re tending a backyard garden or managing several acres, understanding your soil, choosing the right inputs, and planning around unpredictable weather shouldn’t require expensive software or an agronomy degree.</p><p>We’re building Plantly to turn complicated agricultural data into practical, research-backed growing plans—helping growers make informed decisions, avoid unnecessary spending, and care for their soil without losing sight of their harvest.</p></div></div>
    <h3 className="bridge-title">From guesswork to a growing plan.</h3><ol className="comparisons">{comparisons.map(([title,...columns], index)=><li key={title}><h4><span>0{index+1}</span> {title}</h4><div className="comparison-columns">{columns.map((copy,i)=><div key={copy}><span className="eyebrow">{["The challenge","The usual approach","With Plantly"][i]}</span><p>{copy}</p></div>)}</div></li>)}</ol>
    <h3 className="audience-title">Built for the people who grow our food—and their own.</h3><div className="audiences"><div><h4>Home gardeners</h4><p>From a raised bed to a backyard garden, understand what your soil needs and make the most of your growing budget.</p></div><div><h4>Small &amp; mid-sized growers</h4><p>For market gardens and family farms managing multiple plots, make rotation, input, and timing choices with a clearer plan and more visible trade-offs.</p></div></div><a className="text-link" href="#features">Explore Plantly’s tools ↗</a></section>
    <section id="features" className="section wrap" aria-labelledby="features-title"><div className="section-heading"><p className="eyebrow">Key Features</p><h2 id="features-title">Smart Tools for Modern<br />Farming <em>Operations</em></h2><p>In development. Previews show unavailable data, not live results.</p></div><div className="feature-grid">{features.map(([title,description,art,values])=><article className="feature-card" key={title}><h3>{title}</h3><p>{description}</p><MissingAsset>{art} Tall photographic crop.</MissingAsset><div className="preview"><p className="eyebrow">Concept preview</p>{values.map(value=><p key={value}>{value}</p>)}</div></article>)}</div></section>
    <Benefits />
  </main><footer><div className="wrap footer-grid"><div><Link className="footer-brand" href="/" aria-label="Plantly home"><Image src="/assets/images/planty_logo.svg" width={64} height={64} alt="" />Plantly</Link><p>Research-backed growing plans to make smarter decisions from soil to harvest.</p><div className="newsletter"><h3>Get growing insights by email</h3><p>Coming soon. Newsletter signup is not available.</p></div></div><div className="footer-links"><div><h3>Company</h3><a href="#mission">Our Mission</a><a href="#benefits">Benefits</a></div><div><h3>Platform</h3><a href="#features">Key Features</a><a href="#availability">Start Planning</a><a href="#pricing">Pricing</a></div><div><h3>Resources</h3><p>Research and help resources are not available yet.</p></div></div><div className="availability" id="availability"><h3>Planning &amp; sign up</h3><p>Plantly is in development. Planning and account creation are not available on this preview. No personal data is collected here.</p><h3 id="pricing">Pricing</h3><p>Pricing and trial terms are not yet approved. No subscription or payment is offered.</p><p>Planning support is not certified professional agronomic advice. Savings, yields, and reduced irrigation are not guaranteed.</p></div><div className="legal"><span>© {new Date().getFullYear()} Plantly. All rights reserved.</span><span>Terms of Service &amp; Privacy Policy — pending publication.</span></div></div></footer></>;
}
