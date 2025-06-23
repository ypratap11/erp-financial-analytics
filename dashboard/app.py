"""
ERP Financial Analytics Dashboard
Enterprise-grade financial insights and analytics platform
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta, date
import calendar
from typing import Dict, List, Any
import json

# Configure page
st.set_page_config(
    page_title="ERP Financial Analytics",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    color: #1e3a8a;
    text-align: center;
    margin-bottom: 2rem;
    font-weight: bold;
}

.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1.5rem;
    border-radius: 1rem;
    color: white;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.1);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: bold;
    margin-bottom: 0.5rem;
}

.metric-label {
    font-size: 1rem;
    opacity: 0.9;
}

.dashboard-section {
    background-color: #f8fafc;
    padding: 2rem;
    border-radius: 1rem;
    margin-bottom: 2rem;
    border: 1px solid #e2e8f0;
}

.kpi-positive { color: #059669; font-weight: bold; }
.kpi-negative { color: #dc2626; font-weight: bold; }
.kpi-neutral { color: #6b7280; font-weight: bold; }

.sidebar-header {
    background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%);
    color: white;
    padding: 1rem;
    border-radius: 0.5rem;
    text-align: center;
    margin-bottom: 1rem;
}
</style>
""", unsafe_allow_html=True)


# Sample financial data generator
@st.cache_data
def generate_financial_data():
    """Generate comprehensive sample financial data for demonstration"""

    # Date range for the last 24 months
    end_date = datetime.now()
    start_date = end_date - timedelta(days=730)
    date_range = pd.date_range(start=start_date, end=end_date, freq='M')

    # Generate P&L data
    np.random.seed(42)

    revenue_base = 50000000  # $50M annual revenue
    monthly_revenue = []

    for i, month in enumerate(date_range):
        # Add seasonality and growth trend
        seasonal_factor = 1 + 0.1 * np.sin(2 * np.pi * month.month / 12)
        growth_factor = 1 + (i * 0.005)  # 0.5% monthly growth
        random_factor = np.random.normal(1, 0.1)

        monthly_rev = (revenue_base / 12) * seasonal_factor * growth_factor * random_factor
        monthly_revenue.append(max(monthly_rev, 0))

    # Generate expense categories
    pl_data = []
    for i, (month, revenue) in enumerate(zip(date_range, monthly_revenue)):
        # Calculate expenses as percentages of revenue with some variance
        cogs = revenue * np.random.normal(0.35, 0.02)  # 35% ± 2%
        salaries = revenue * np.random.normal(0.25, 0.01)  # 25% ± 1%
        marketing = revenue * np.random.normal(0.08, 0.02)  # 8% ± 2%
        rd = revenue * np.random.normal(0.12, 0.01)  # 12% ± 1%
        operations = revenue * np.random.normal(0.06, 0.01)  # 6% ± 1%
        other_expenses = revenue * np.random.normal(0.04, 0.01)  # 4% ± 1%

        total_expenses = cogs + salaries + marketing + rd + operations + other_expenses
        gross_profit = revenue - cogs
        net_profit = revenue - total_expenses

        pl_data.append({
            'Period': month,
            'Year': month.year,
            'Month': month.month,
            'Month_Name': calendar.month_name[month.month],
            'Quarter': f"Q{((month.month - 1) // 3) + 1}",
            'Revenue': revenue,
            'COGS': cogs,
            'Gross_Profit': gross_profit,
            'Salaries': salaries,
            'Marketing': marketing,
            'R&D': rd,
            'Operations': operations,
            'Other_Expenses': other_expenses,
            'Total_Expenses': total_expenses,
            'Net_Profit': net_profit,
            'Gross_Margin_%': (gross_profit / revenue) * 100,
            'Net_Margin_%': (net_profit / revenue) * 100,
        })

    df_pl = pd.DataFrame(pl_data)

    # Generate budget data (10% higher than actual for demo)
    df_budget = df_pl.copy()
    budget_variance = np.random.normal(1.1, 0.05, len(df_budget))
    df_budget['Budget_Revenue'] = df_budget['Revenue'] * budget_variance
    df_budget['Budget_Net_Profit'] = df_budget['Net_Profit'] * budget_variance

    # Generate cash flow data
    cash_flow_data = []
    cash_balance = 10000000  # Starting with $10M cash

    for _, row in df_pl.iterrows():
        operating_cash = row['Net_Profit'] + np.random.normal(500000, 100000)  # Add depreciation, etc.
        investing_cash = np.random.normal(-200000, 50000)  # CapEx
        financing_cash = np.random.normal(-100000, 200000)  # Debt/equity changes

        net_cash_flow = operating_cash + investing_cash + financing_cash
        cash_balance += net_cash_flow

        cash_flow_data.append({
            'Period': row['Period'],
            'Operating_Cash_Flow': operating_cash,
            'Investing_Cash_Flow': investing_cash,
            'Financing_Cash_Flow': financing_cash,
            'Net_Cash_Flow': net_cash_flow,
            'Cash_Balance': cash_balance
        })

    df_cash_flow = pd.DataFrame(cash_flow_data)

    return df_pl, df_budget, df_cash_flow


def create_kpi_metrics(df_current, df_previous):
    """Create KPI metrics with period-over-period comparison"""

    current_revenue = df_current['Revenue'].sum()
    previous_revenue = df_previous['Revenue'].sum()
    revenue_growth = ((current_revenue - previous_revenue) / previous_revenue) * 100

    current_profit = df_current['Net_Profit'].sum()
    previous_profit = df_previous['Net_Profit'].sum()
    profit_growth = ((current_profit - previous_profit) / previous_profit) * 100 if previous_profit != 0 else 0

    current_margin = (df_current['Net_Profit'].sum() / df_current['Revenue'].sum()) * 100
    previous_margin = (df_previous['Net_Profit'].sum() / df_previous['Revenue'].sum()) * 100
    margin_change = current_margin - previous_margin

    current_cash = df_current['Revenue'].sum() * 0.15  # Simplified cash calculation

    return {
        'revenue': {'value': current_revenue, 'growth': revenue_growth},
        'profit': {'value': current_profit, 'growth': profit_growth},
        'margin': {'value': current_margin, 'change': margin_change},
        'cash': {'value': current_cash, 'growth': 5.2}  # Placeholder
    }


def create_revenue_trend_chart(df):
    """Create revenue trend visualization"""
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Revenue trend
    fig.add_trace(
        go.Scatter(
            x=df['Period'],
            y=df['Revenue'],
            mode='lines+markers',
            name='Monthly Revenue',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=8)
        ),
        secondary_y=False
    )

    # Net margin trend
    fig.add_trace(
        go.Scatter(
            x=df['Period'],
            y=df['Net_Margin_%'],
            mode='lines+markers',
            name='Net Margin %',
            line=dict(color='#10b981', width=2),
            marker=dict(size=6)
        ),
        secondary_y=True
    )

    # Add trend line
    z = np.polyfit(range(len(df)), df['Revenue'], 1)
    trend_line = np.poly1d(z)(range(len(df)))

    fig.add_trace(
        go.Scatter(
            x=df['Period'],
            y=trend_line,
            mode='lines',
            name='Revenue Trend',
            line=dict(color='#ef4444', width=2, dash='dash'),
            opacity=0.7
        ),
        secondary_y=False
    )

    fig.update_xaxes(title_text="Period")
    fig.update_yaxes(title_text="Revenue ($)", secondary_y=False)
    fig.update_yaxes(title_text="Net Margin (%)", secondary_y=True)

    fig.update_layout(
        title="Revenue Growth & Profitability Trend",
        hovermode='x unified',
        height=400,
        showlegend=True
    )

    return fig


def create_pl_waterfall_chart(df_current):
    """Create P&L waterfall chart"""

    total_revenue = df_current['Revenue'].sum()
    total_cogs = df_current['COGS'].sum()
    total_salaries = df_current['Salaries'].sum()
    total_marketing = df_current['Marketing'].sum()
    total_rd = df_current['R&D'].sum()
    total_operations = df_current['Operations'].sum()
    total_other = df_current['Other_Expenses'].sum()
    net_profit = df_current['Net_Profit'].sum()

    fig = go.Figure(go.Waterfall(
        name="P&L Analysis",
        orientation="v",
        measure=["absolute", "relative", "relative", "relative", "relative", "relative", "relative", "total"],
        x=["Revenue", "COGS", "Salaries", "Marketing", "R&D", "Operations", "Other", "Net Profit"],
        textposition="outside",
        text=[f"${total_revenue / 1e6:.1f}M", f"-${total_cogs / 1e6:.1f}M", f"-${total_salaries / 1e6:.1f}M",
              f"-${total_marketing / 1e6:.1f}M", f"-${total_rd / 1e6:.1f}M", f"-${total_operations / 1e6:.1f}M",
              f"-${total_other / 1e6:.1f}M", f"${net_profit / 1e6:.1f}M"],
        y=[total_revenue, -total_cogs, -total_salaries, -total_marketing, -total_rd, -total_operations, -total_other,
           net_profit],
        connector={"line": {"color": "rgb(63, 63, 63)"}},
        decreasing={"marker": {"color": "#ef4444"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#3b82f6"}}
    ))

    fig.update_layout(
        title="Profit & Loss Waterfall Analysis",
        height=500,
        showlegend=False
    )

    return fig


def create_budget_variance_chart(df_pl, df_budget):
    """Create budget vs actual variance analysis"""

    # Get last 12 months for comparison
    df_recent = df_pl.tail(12).copy()
    df_budget_recent = df_budget.tail(12).copy()

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Revenue: Budget vs Actual', 'Profit: Budget vs Actual'),
        vertical_spacing=0.1
    )

    # Revenue comparison
    fig.add_trace(
        go.Bar(
            x=df_recent['Month_Name'],
            y=df_budget_recent['Budget_Revenue'],
            name='Budget Revenue',
            marker_color='lightblue',
            opacity=0.7
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=df_recent['Month_Name'],
            y=df_recent['Revenue'],
            name='Actual Revenue',
            marker_color='#3b82f6'
        ),
        row=1, col=1
    )

    # Profit comparison
    fig.add_trace(
        go.Bar(
            x=df_recent['Month_Name'],
            y=df_budget_recent['Budget_Net_Profit'],
            name='Budget Profit',
            marker_color='lightgreen',
            opacity=0.7,
            showlegend=False
        ),
        row=2, col=1
    )

    fig.add_trace(
        go.Bar(
            x=df_recent['Month_Name'],
            y=df_recent['Net_Profit'],
            name='Actual Profit',
            marker_color='#10b981',
            showlegend=False
        ),
        row=2, col=1
    )

    fig.update_layout(
        title="Budget vs Actual Performance Analysis",
        height=600,
        barmode='group'
    )

    return fig


def create_cash_flow_chart(df_cash):
    """Create cash flow analysis chart"""

    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Cash Flow Components', 'Cash Balance Trend'),
        vertical_spacing=0.15
    )

    # Cash flow components
    fig.add_trace(
        go.Bar(
            x=df_cash['Period'],
            y=df_cash['Operating_Cash_Flow'],
            name='Operating CF',
            marker_color='#10b981'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=df_cash['Period'],
            y=df_cash['Investing_Cash_Flow'],
            name='Investing CF',
            marker_color='#f59e0b'
        ),
        row=1, col=1
    )

    fig.add_trace(
        go.Bar(
            x=df_cash['Period'],
            y=df_cash['Financing_Cash_Flow'],
            name='Financing CF',
            marker_color='#ef4444'
        ),
        row=1, col=1
    )

    # Cash balance trend
    fig.add_trace(
        go.Scatter(
            x=df_cash['Period'],
            y=df_cash['Cash_Balance'],
            mode='lines+markers',
            name='Cash Balance',
            line=dict(color='#3b82f6', width=3),
            marker=dict(size=6),
            showlegend=False
        ),
        row=2, col=1
    )

    fig.update_layout(
        title="Cash Flow Analysis",
        height=600,
        barmode='relative'
    )

    return fig


def main():
    # Header
    st.markdown('<h1 class="main-header">💰 ERP Financial Analytics Dashboard</h1>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown('<div class="sidebar-header"><h3>📊 Financial Controls</h3></div>', unsafe_allow_html=True)

        # Period selection
        view_type = st.selectbox(
            "Analysis Period",
            ["Last 12 Months", "Year-to-Date", "Last 24 Months", "Custom Range"]
        )

        # Company selection (for demo)
        company = st.selectbox(
            "Business Unit",
            ["Consolidated", "North America", "Europe", "Asia Pacific"]
        )

        # Currency selection
        currency = st.selectbox(
            "Currency",
            ["USD", "EUR", "GBP", "JPY"]
        )

        # Refresh button
        if st.button("🔄 Refresh Data", type="primary"):
            st.cache_data.clear()
            st.rerun()

    # Load data
    with st.spinner("Loading financial data..."):
        df_pl, df_budget, df_cash_flow = generate_financial_data()

    # Filter data based on selection
    if view_type == "Last 12 Months":
        df_current = df_pl.tail(12)
        df_previous = df_pl.iloc[-24:-12] if len(df_pl) >= 24 else df_pl.head(12)
    elif view_type == "Year-to-Date":
        current_year = datetime.now().year
        df_current = df_pl[df_pl['Year'] == current_year]
        df_previous = df_pl[df_pl['Year'] == current_year - 1]
    else:  # Last 24 months or custom
        df_current = df_pl.tail(12)
        df_previous = df_pl.iloc[-24:-12] if len(df_pl) >= 24 else df_pl.head(12)

    # Calculate KPIs
    kpis = create_kpi_metrics(df_current, df_previous)

    # KPI Section
    st.markdown("## 📈 Key Performance Indicators")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        revenue_color = "kpi-positive" if kpis['revenue']['growth'] > 0 else "kpi-negative"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${kpis['revenue']['value'] / 1e6:.1f}M</div>
            <div class="metric-label">Total Revenue</div>
            <div class="{revenue_color}">↗ {kpis['revenue']['growth']:+.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        profit_color = "kpi-positive" if kpis['profit']['growth'] > 0 else "kpi-negative"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${kpis['profit']['value'] / 1e6:.1f}M</div>
            <div class="metric-label">Net Profit</div>
            <div class="{profit_color}">↗ {kpis['profit']['growth']:+.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        margin_color = "kpi-positive" if kpis['margin']['change'] > 0 else "kpi-negative"
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{kpis['margin']['value']:.1f}%</div>
            <div class="metric-label">Net Margin</div>
            <div class="{margin_color}">↗ {kpis['margin']['change']:+.1f}pp</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">${kpis['cash']['value'] / 1e6:.1f}M</div>
            <div class="metric-label">Cash Position</div>
            <div class="kpi-positive">↗ {kpis['cash']['growth']:+.1f}%</div>
        </div>
        """, unsafe_allow_html=True)

    # Main Analysis Section
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Revenue Analysis", "💰 P&L Breakdown", "📊 Budget Variance", "💸 Cash Flow"])

    with tab1:
        st.markdown("### Revenue Growth & Profitability Trends")
        fig_revenue = create_revenue_trend_chart(df_pl.tail(24))
        st.plotly_chart(fig_revenue, use_container_width=True)

        # Revenue insights
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 Revenue Insights")
            recent_growth = ((df_current['Revenue'].sum() - df_previous['Revenue'].sum()) / df_previous[
                'Revenue'].sum()) * 100
            avg_monthly = df_current['Revenue'].mean()
            st.write(f"• **Growth Rate**: {recent_growth:+.1f}% vs previous period")
            st.write(f"• **Average Monthly**: ${avg_monthly / 1e6:.1f}M")
            st.write(f"• **Peak Month**: {df_current.loc[df_current['Revenue'].idxmax(), 'Month_Name']}")
            st.write(f"• **Revenue Run Rate**: ${avg_monthly * 12 / 1e6:.1f}M annually")

        with col2:
            st.markdown("#### 🎯 Profitability Metrics")
            avg_gross_margin = df_current['Gross_Margin_%'].mean()
            avg_net_margin = df_current['Net_Margin_%'].mean()
            st.write(f"• **Gross Margin**: {avg_gross_margin:.1f}%")
            st.write(f"• **Net Margin**: {avg_net_margin:.1f}%")
            st.write(f"• **Profit per Employee**: ${(df_current['Net_Profit'].sum() / 1000) / 1e3:.0f}K (est.)")
            st.write(f"• **Operating Leverage**: Strong margin expansion")

    with tab2:
        st.markdown("### Profit & Loss Analysis")
        fig_waterfall = create_pl_waterfall_chart(df_current)
        st.plotly_chart(fig_waterfall, use_container_width=True)

        # Expense breakdown
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 💡 Expense Analysis")
            total_revenue = df_current['Revenue'].sum()
            cogs_pct = (df_current['COGS'].sum() / total_revenue) * 100
            salary_pct = (df_current['Salaries'].sum() / total_revenue) * 100
            marketing_pct = (df_current['Marketing'].sum() / total_revenue) * 100

            st.write(f"• **COGS**: {cogs_pct:.1f}% of revenue")
            st.write(f"• **Salaries**: {salary_pct:.1f}% of revenue")
            st.write(f"• **Marketing**: {marketing_pct:.1f}% of revenue")
            st.write(f"• **R&D**: {(df_current['R&D'].sum() / total_revenue) * 100:.1f}% of revenue")

        with col2:
            # Expense trend chart
            expense_data = {
                'Category': ['COGS', 'Salaries', 'Marketing', 'R&D', 'Operations', 'Other'],
                'Amount': [
                    df_current['COGS'].sum(),
                    df_current['Salaries'].sum(),
                    df_current['Marketing'].sum(),
                    df_current['R&D'].sum(),
                    df_current['Operations'].sum(),
                    df_current['Other_Expenses'].sum()
                ]
            }

            fig_expenses = px.pie(
                values=expense_data['Amount'],
                names=expense_data['Category'],
                title="Expense Breakdown"
            )
            st.plotly_chart(fig_expenses, use_container_width=True)

    with tab3:
        st.markdown("### Budget vs Actual Performance")
        fig_variance = create_budget_variance_chart(df_pl, df_budget)
        st.plotly_chart(fig_variance, use_container_width=True)

        # Variance analysis
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### 📊 Revenue Variance")
            budget_rev = df_budget.tail(12)['Budget_Revenue'].sum()
            actual_rev = df_current['Revenue'].sum()
            rev_variance = ((actual_rev - budget_rev) / budget_rev) * 100

            variance_color = "🟢" if rev_variance > 0 else "🔴"
            st.write(f"{variance_color} **Variance**: {rev_variance:+.1f}%")
            st.write(f"• **Budget**: ${budget_rev / 1e6:.1f}M")
            st.write(f"• **Actual**: ${actual_rev / 1e6:.1f}M")
            st.write(f"• **Difference**: ${(actual_rev - budget_rev) / 1e6:+.1f}M")

        with col2:
            st.markdown("#### 💰 Profit Variance")
            budget_profit = df_budget.tail(12)['Budget_Net_Profit'].sum()
            actual_profit = df_current['Net_Profit'].sum()
            profit_variance = ((actual_profit - budget_profit) / budget_profit) * 100

            variance_color = "🟢" if profit_variance > 0 else "🔴"
            st.write(f"{variance_color} **Variance**: {profit_variance:+.1f}%")
            st.write(f"• **Budget**: ${budget_profit / 1e6:.1f}M")
            st.write(f"• **Actual**: ${actual_profit / 1e6:.1f}M")
            st.write(f"• **Difference**: ${(actual_profit - budget_profit) / 1e6:+.1f}M")

    with tab4:
        st.markdown("### Cash Flow Analysis")
        df_cash_recent = df_cash_flow.tail(12)
        fig_cash = create_cash_flow_chart(df_cash_recent)
        st.plotly_chart(fig_cash, use_container_width=True)

        # Cash flow metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown("#### 💵 Operating Cash Flow")
            operating_cf = df_cash_recent['Operating_Cash_Flow'].sum()
            st.metric("12-Month Total", f"${operating_cf / 1e6:.1f}M")
            st.write(f"• **Monthly Average**: ${operating_cf / 12 / 1e6:.1f}M")
            st.write(f"• **CF Conversion**: {(operating_cf / df_current['Net_Profit'].sum()) * 100:.0f}%")

        with col2:
            st.markdown("#### 📈 Investing Activities")
            investing_cf = df_cash_recent['Investing_Cash_Flow'].sum()
            st.metric("12-Month Total", f"${investing_cf / 1e6:.1f}M")
            st.write(f"• **Monthly Average**: ${investing_cf / 12 / 1e6:.1f}M")
            st.write(f"• **% of Revenue**: {(abs(investing_cf) / df_current['Revenue'].sum()) * 100:.1f}%")

        with col3:
            st.markdown("#### 🏦 Cash Position")
            current_cash = df_cash_recent['Cash_Balance'].iloc[-1]
            st.metric("Current Balance", f"${current_cash / 1e6:.1f}M")
            st.write(f"• **Days of Expenses**: {(current_cash / (df_current['Total_Expenses'].sum() / 365)):.0f} days")
            st.write(f"• **Cash Ratio**: Strong liquidity position")

    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666;">
        <p>🏢 <strong>ERP Financial Analytics</strong> | Real-time Business Intelligence</p>
        <p>Data as of: {}</p>
    </div>
    """.format(datetime.now().strftime("%B %d, %Y at %I:%M %p")), unsafe_allow_html=True)


if __name__ == "__main__":
    main()