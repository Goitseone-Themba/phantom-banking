import PhantomBankingSvg from '../../assets/phantom-banking.svg';
export function PhantomBankingLogo() {
    return (
        <>
            <div style={
                {
                    display: 'flex',
                    flexWrap: 'nowrap',
                    width: 'inherit',
                    justifyContent: 'center',
                    
                }
            }>
                <img src={PhantomBankingSvg} alt='Phantom Banking Logo Image'></img>
            </div>
        </>
    )
}
