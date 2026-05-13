from main import execute_dashboard, main


def test_execute_dashboard_success_with_valid_dashboard_visualization_execution(mocker):
    """Tests that no exception is raised when the dashboard visualization is successfully executed."""
    fake_data = "fake_config"
    fake_engine = "fake_engine"
    fake_quant_dict = {
        "portfolio_percentage_changes": [1, 2, 3],
        "portfolio_mean": 0,
        "portfolio_vol": 1,
        "var_value": 100.50,
        "confidence_level": 0.99
    }

    mocker.patch('main.get_js_config', return_value=fake_data)
    mocker.patch('main.get_db_engine', return_value=fake_engine)
    mock_etl = mocker.patch('main.run_etl_pipeline')
    mock_quant = mocker.patch('main.run_quant_engine', return_value=fake_quant_dict)
    mock_plot = mocker.patch('main.plot_return_density_with_var')

    execute_dashboard()

    mock_etl.assert_called_once_with(fake_data, fake_engine)
    mock_quant.assert_called_once_with(fake_data, fake_engine)
    mock_plot.assert_called_once_with([1, 2, 3], 0, 1, 100.50, 0.99)


def test_main_success_with_valid_dashboard_application_execution(mocker):
    """Tests that no exception is raised when the dashboard application is successfully executed."""
    mock_execute_dashboard = mocker.patch('main.execute_dashboard')
    mock_logger = mocker.patch('main.logger.info')

    main()

    mock_execute_dashboard.assert_called_once()
    assert mock_logger.call_count == 2